# ping

对库`ping3`的封装

```python
def ping(target, timeout=timedelta(seconds=0.75))-> float: # ms

class Pings(Producer):
    res: dict[str, float] # ms
```

### Pings

同时ping多个网站，并返回结果`dict`