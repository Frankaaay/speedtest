# GUI

使用`StdoutRedirector`类将标准输出和标准错误重定向到一个滚动文本框中以便在GUI中显示监测过程中的输出信息。

`Result2Table`用于将数据显示到表格

所有GUI都可以独立运行

## `toolkit`

主文件，包含所有GUI的入口函数

### `toolkit`与其他GUI的交互

`toolkit`通过调用`gui_any.main(content_frame)`传递一个`tk.Frame`启动子模块GUI的初始化

`toolkit`通过检查`gui_any.IS_RUNNING`来判断子模块GUI是否正在运行，并保同时只有一个子模块GUI在运行，并在子模块GUI关闭后销毁

## gui_live

 - 实时监测直播状态
 - 记录网速
 - 记录设备状态和测试结果
 - 多种直播平台和浏览器选择
 - 正/倒计时

### TODO
 - [ ] 未正常启动时的提示

## gui_*

均为简单图形化包装
