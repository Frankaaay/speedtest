from common import *
from .api import *
from .at import AT

class Panel_FM(Panel):
    def __init__(self, device_ip, timeout=timedelta(seconds=30)):
        super().__init__(device_ip, timeout)

    def update(self):
        res = {}
        at = AT(self.ip, self.timeout)

        x = at.sr1('AT*BANDIND?')
        if x.startswith('*BANDIND: '):
            x = x[len('*BANDIND: '):].split(',')
            res['band'] = x[1].strip()
        else:
            print(f"Error: AT*BANDIND? => {x}")


        # +CESQ: <rxlev>,<ber>,<rscp>,<ecno>,<rsrq>,<rsrp>,<sinr>
        x = at.sr1('AT*CESQ')
        if x.startswith('*CESQ: '):
            x = x[len('*CESQ: '):].split(',')

            rxlev = int(x[0])
            if 0 <= rxlev <= 63:
                res['rssi'] = rxlev - 110

            ber = int(x[1])
            if 0 <= ber <= 7:
                res['ber'] = ber

            rscp = int(x[2])
            if 0 <= rscp <= 96:
                res['rscp'] = rscp - 121

            rsrq = int(x[4])
            if 0 <= rsrq <= 34:
                res['rsrq'] = rsrq * 0.5 - 20
            
            rsrp = int(x[5])
            if 0 <= rsrp <= 97:
                res['rsrp'] = rsrp - 141

            sinr = int(x[6])
            res['sinr'] = sinr

        else:   
            print(f"Error: AT*CESQ => {x}")

        x = at.sr1('AT+RSRP?')
        if x.startswith('+RSRP: '):
            x = x[len('+RSRP: '):].split(',')
            res['pci'] = x[0]
            res['earfcn'] = x[1]
            # res['rsrp'] = x[2]
        else:
            print(f"Error: AT+RSRP? => {x}")

        # x = at.sr1('AT+RSRQ?')
        # if x.startswith('+RSRQ: '):
        #     x = x[len('+RSRQ: '):].split(',')
        #     res['rsrq'] = x[2]
        # else:
        #     print(f"Error: AT+RSRQ? => {x}")
        
        super().update()
        self.res = PanelState(res)

    def set_band(self, band:int|None = 0):
        raise NotImplementedError()
        at = AT(self.ip,self.timeout)
        if band is None:
            res = at.sr1(f'AT*BAND={band}')
        elif band < 0 or band > 4:
            pass
        return res
    
    def reboot(self):
        raise NotImplementedError()
    
    def reset(self):
        at = AT(self.ip,self.timeout)
        res = at.sr1('AT*RESET')
        return res
        
