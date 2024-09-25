# Sequence

```python
class Sequence(
    Thread,
    Producer,
):
    def __init__(self, obj: Producer, interval: timedelta):...

    def update(self):...

    def run(self):...

    def flush(self):...
```

`Sequence`接受一个`Producer`对象和一个时间间隔，并周期性地调用`Producer`的`update`方法。

`Sequence`实现了`Producer`接口，可视为一个周期性产生结果的`Producer`。