import tkinter as tk
import common

from idlelib.util import fix_win_hidpi  # noqa: F401


class StdoutRedirector:
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.config(state="normal")  # 允许编辑
        self.text_widget.insert(tk.END, message)  # 在文本框末尾插入消息
        self.text_widget.see(tk.END)
        # 删除多余的行
        lines = self.text_widget.get("1.0", tk.END).split("\n")
        if len(lines) > 100:
            self.text_widget.delete("1.0", f"{len(lines) - 100}.0")
        self.text_widget.config(state="disabled")  # 禁止编辑

    def flush(self):
        pass

    def close(self):
        pass


class StopCounter(common.Recorder):
    """
    记录运行次数，当达到目标次数时停止运行
    """

    def __init__(self, callback_each, callback_final, target_cnt):
        super().__init__(None)
        self.cnt = 0
        self.callback_each = callback_each
        self.callback_final = callback_final
        self.target_cnt = target_cnt
        self.callback_each(0)

    def record(self, any):
        super().record(any)
        self.cnt += 1
        self.callback_each(self.cnt)
        if self.target_cnt > 0 and self.cnt >= self.target_cnt:
            self.callback_final()
