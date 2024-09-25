# Iperf

对`iperf3`的封装，使用同目录下的`iperf3/iperf3.exe`

```python
class ClientTcp(Producer):
    res: float

class ClientUdp(Producer):
    res: float
```

值得注意的是`iperf`的`Mb/s`是`bit/s`/`1e6`而不是`1<<20`得出的

## TODO

- [ ] 输出重定向到GUI
- [ ] 不弹出新窗口
- [ ] iperf3服务段偶尔会卡住在错误中死循环