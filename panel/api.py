from common import *

INVALID_VALUE = '-'

class PanelState:
    '''
    本质上就是字典
    '''
    def __init__(self, data: dict={}):
        self.data = data

    def __getattr__(self, name):
        self.get(name)
    def __getitem__(self, name):
        self.get(name)

    def __str__(self):
        return ' '.join(f'{k}:{v}' for k,v in self.data.items())
    
    def get(self, name):
        return str(self.data.get(name, INVALID_VALUE))
    

class Panel(Producer):
    def __init__(self, device_ip, timeout=timedelta(seconds=5)):
        super().__init__()
        self.ip = device_ip
        self.timeout = timeout.total_seconds()
        self.set_default(PanelState())

    def update(self):
        super().update()


class Console(Recorder):
    def __init__(self, file: TextIOWrapper):
        super().__init__(file)

    def record(self, res: PanelState):
        self.file.write(str(res)+'\n')
        