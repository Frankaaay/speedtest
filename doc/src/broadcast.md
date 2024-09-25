# 设备发现


```python
class Broadcast(Producer):...
    res: list[tuple[str, int]]
```

使用组播的方式，设备在局域网内广播自己的信息，其他设备通过监听组播消息，获取同时在线的设备

`res`为在线的设备列表，每个设备为一个字符串，格式为`(ip,port)`

## TODO
- [ ] 指定发送的网络接口