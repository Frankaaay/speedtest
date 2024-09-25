# Recorder

```python

class Recorder:
    def __init__(self, file: io.TextIOWrapper):...

    def record(self, res) -> None:...

    def flush(self):...

    def close(self):...
```


```python
class Console(Recorder):
    pass
```
在各个库下的`Console`和`Reporter`分别是以终端、文件为输出目标的`Recorder`实现。