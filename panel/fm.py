from common import *
from .api import *
from .at import AT

class Panel_FM(Panel):
    def __init__(self, device_ip, timeout=timedelta(seconds=10), logger=sys.stderr):
        super().__init__(device_ip, timeout)
        self.logger = logger

    def update(self):
        res = {}
        at = AT(self.ip, self.timeout)
        if at.error:
            self.logger.write(f"[设备]连不到！\n")
            return
        try:
            ok = at.sr1("AT")
            if ok != "OK":
                self.logger.write(f"[设备]AT寄了! {ok}\n")
                self.res = PanelState({})
        except Exception as e:
            self.logger.write(f"[设备]寄了! \n{e}")
            return
        
        res = at.BANDIND()
        res.update(at.CESQ())
        res.update(at.RSRP())
        self.res = PanelState(res)
        super().update()

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
        
