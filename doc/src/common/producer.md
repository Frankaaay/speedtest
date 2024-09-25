# Producer

```python
class Producer:
    """
    生产者，用于产生数据
    """

    def __init__(self):
        self.res = None
        self.recorders: list[Recorder] = []
        self.stopped = False
        self.ttl = float("inf")
        self.last_update = time()
        self.default = None

    def set_ttl(self, ttl: timedelta):...

    def set_default(self, default):...

    def update(self) -> None:...

    def get(self):  # -> Any:...

    def add_recorder(self, recorder: Recorder):..

    def record(self) -> None:...

    def stop(self) -> None:...

    def flush(self) -> None:...

```

## 属性

### `res`

生产者产生的数据。

### `recorders`

记录器列表，用于记录生产者产生的数据。

### `stopped`

生产者是否已经停止产生数据。

### `ttl`

生产者数据的保质期。

### `last_update`

生产者最后一次更新数据的时间。

### `default`

数据过期时返回的默认值。

## 方法

### `set_ttl(self, ttl: timedelta)`

设置生产者数据的保质期。

### `set_default(self, default)`

设置生产者的默认值。

### `update(self) -> None`

产生新数据，这个方法应该被**继承**。

### `get(self) -> Any`

获取生产者数。

### `add_recorder(self, recorder: Recorder)`

添加记录器。

### `record(self) -> None`

记录生产者产生的数据。

### `stop(self) -> None`

停止生产者产生数据。

### `flush(self) -> None`

记录器刷写到文件。


# AutoFlush
```python
class AutoFlush(Producer):
    def __init__(self, obj: Producer, interval: timedelta):...
```

自动刷写到文件