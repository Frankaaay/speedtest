# 设备信息

通过AT指令获取设备信息

```python
class PanelState(dict):
    pass 

class AT:
    error:bool
    def __init__(self, device_ip, timeout: float):...

    def sr1(self, cmd: str) -> str:...

class Panel(Producer):
    res: PanelState

class Panel_FM(Panel):
    pass
```

`AT`持有一条TCP连接，通过`sr1`发送和接受一条AT指令，`error`指示连接出错

目前只为FM实现了`Panel`类~~，可能会根据需求添加其他设备~~

## TODO

- [ ] 其他品牌信息的获取
- [ ] 添加其他AT指令: 锁频
- [x] 添加其他AT指令: 重启/重置
- [ ] 添加其他AT指令: 射频信息

## 如何添加新的AT指令获取更多信息

1. 在`AT`类中添加新的命令
2. 在`Panel_FM.update`中调用
3. 修改`common.DEVICE_INFOS`在以在日志中记录
4. 修改`server_live.IN_LINES`或`server_live.IN_HOVERTEXT`在以网页中显示