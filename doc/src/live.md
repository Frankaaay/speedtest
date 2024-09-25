# 直播

也不全是直播，不管了

通过检查html元素，判断直播卡顿情况

大部分逻辑在处理异常

## 站点

目前支持的站点有
- [B站](https://live.bilibili.com/)
- [抖音](https://live.douyu.com/)
- [西瓜视频](https://www.ixigua.com/)

同时`EmptyLive`提供一个空浏览器，可以用于调试

## API

```python
class LiveState:
    Normal # 正常
    Stuck  # 卡顿
    End    # 结束
    Error
    Afk    

class Live(Producer):
    res: tuple[LiveState, str | None]
    def __init__(
        self,
        browser_name,
        base_url,
        room_id,
        ...
    ):...

    def find_available(self, get_url: Callable[[webdriver.Edge], str]):...

    def goto_room(self, room_id: str):...

    def refresh(self):...

    def update(self):...

    def stop(self):...

```

### AFK

部分站点有afk检测，定时刷新直播间，刷新期间此时`LiveState.Afk`

**注意**`LiveState.Afk`出现时带宽记录会暂停，为了减小影响，带宽会重复之前的记录


### `find_available(get_url: Callable[[webdriver.Edge], str])`

寻找可用的直播间，`get_url`是从`base_url`上获取直播链接的函数，返回URL
