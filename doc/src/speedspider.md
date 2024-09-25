# 测速

有问题找陈。

目前测速强依赖于各个“高校测速网”，但部分网站可能不稳定。

- [上海交通大学](http://wsus.sjtu.edu.cn/speedtest/)
- [~~东北大学~~](http://speed.neu.edu.cn/)
- [中国科学技术大学](http://test.ustc.edu.cn/)
- [~~南京大学~~](http://test.nju.edu.cn/)
- [南京航空航天大学](http://speed.nuaa.edu.cn/)

```python
class SpeedTestResult:
    lag: float
    jit: float
    dl: float
    ul: float

class SpeedTester(Producer):
    res: SpeedTestResult
    asap: bool

class SpeedTester0Interval(Producer):
    res: SpeedTestResult
```
## 完成判断

当`int(driver.execute_script("return s.getState()")) == 4`时说明测速结束。

结果由文本读取

## ASAP(as soon as possible)

当一次测速进行到最后一阶段（上传）时`asap`被设置，`SpeedTester0Interval`会开始下一次测速

## 异常处理

当测速失败时，`SpeedTestResult`

| 项  | 作用       |
| --- | ---------- |
| lag | 错误类别   |
| jit | 发生的网站 |
| dl  | None       |
| ul  | None       |