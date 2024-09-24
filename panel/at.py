from socket import socket, AF_INET, SOCK_STREAM


class AT:
    def __init__(self, device_ip, timeout: float):
        self.ip = device_ip
        self.timeout = timeout
        self.error = False
        try:
            self.s = socket(AF_INET, SOCK_STREAM)
            self.s.settimeout(self.timeout)
            self.s.connect((self.ip, 8090))
        except TimeoutError:
            print("[AT]连接超时")
            self.error = True

    def sr1(self, cmd: str):
        """
        Send and recv one AT command
        """
        if self.error:
            return "ERR: AT connect fail!"
        self.s.sendall(cmd.encode())
        try:
            res = self.s.recv(80).decode().strip()
            # print(f"{cmd} -> {res}")
            return res
        except TimeoutError:
            print(f"[AT]{cmd}超时")
            return f"ERR: AT command {cmd} timed out"

    def CESQ(self) -> dict:
        # +CESQ: <rxlev>,<ber>,<rscp>,<ecno>,<rsrq>,<rsrp>,<sinr>
        res = {}
        x = self.sr1("AT*CESQ")
        if x.startswith("*CESQ: "):
            x = x[len("*CESQ: ") :].split(",")

            rxlev = int(x[0])
            if 0 <= rxlev <= 63:
                res["rssi"] = rxlev - 110

            ber = int(x[1])
            if 0 <= ber <= 7:
                res["ber"] = ber

            rscp = int(x[2])
            if 0 <= rscp <= 96:
                res["rscp"] = rscp - 121

            rsrq = int(x[4])
            if 0 <= rsrq <= 34:
                res["rsrq"] = rsrq * 0.5 - 20

            rsrp = int(x[5])
            if 0 <= rsrp <= 97:
                res["rsrp"] = rsrp - 141

            sinr = int(x[6])
            res["sinr"] = sinr

        else:
            res["CESQ"] = f"Error: AT*CESQ => {x}"
            print(f"[AT]Error: AT*CESQ => {x}")

        return res

    def RSRP(self) -> dict:
        res = {}
        x = self.sr1("AT+RSRP?")
        if x.startswith("+RSRP: "):
            x = x[len("+RSRP: ") :].split(",")
            res["pci"] = x[0]
            res["earfcn"] = x[1]
            # res['rsrp'] = x[2]
        else:
            res["RSRP"] = f"Error: AT+RSRP? => {x}"
            print(f"[AT]Error: AT+RSRP? => {x}")

        return res

    def BANDIND(self) -> dict:
        res = {}
        x = self.sr1("AT*BANDIND?")
        if x.startswith("*BANDIND: "):
            x = x[len("*BANDIND: ") :].split(",")
            res["band"] = x[1].strip()
        else:
            res["BANDIND"] = f"Error: AT*BANDIND? => {x}"
            print(f"[AT]Error: AT*BANDIND? => {x}")

        return res

    def __del__(self):
        self.s.close()
