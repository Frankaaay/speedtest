# multi3

## 关于multi3

multi3是一个http代理服务器，这里使用其来统计浏览器的实时带宽

multi3读取配置文件`multi3.toml`,将`host`的请求转发到`pool`，在`lookup`提供对应`id`的数据量统计


```python
class ProxyResult:
    upload: float
    download: float

class ProxySpeed(Producer):
    res: ProxyResult
```

**注意**`LiveState.Afk`出现时带宽记录会暂停，为了减小影响，带宽会重复之前的记录