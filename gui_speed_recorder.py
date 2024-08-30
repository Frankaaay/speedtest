import tkinter as tk
from tkinter import ttk
import speedspider
import common
from datetime import timedelta
import speed_recorder

def main():
    def add_item():
        item = add_url.get()
        if item:
            url_listbox.insert(tk.END, item)
            add_url.delete(0, tk.END)
        else:
            pass
            # messagebox.showwarning("警告", "请输入要添加的项！")


    def delete_item():
        selected_index = url_listbox.curselection()
        if selected_index:
            url_listbox.delete(selected_index)
        else:
            pass
            # messagebox.showwarning("警告", "请选择要删除的项！")


    class Result2Display(common.Recorder):
        def __init__(self, table: ttk.Treeview):
            super().__init__(None)
            self.table = table
            self.len = 0

        def record(self, res: speedspider.SpeedTestResult):
            if self.len > 8:
                self.table.delete(self.table.get_children()[0])
            else:
                self.len += 1
            self.table.insert("", tk.END,
                            values=(res.lag, res.jit, res.ul, res.dl))


    def start_button_clicked():
        nonlocal obj, url_listbox, delta_custom, save_log, tree, headless
        if obj is not None:
            return
        delta = timedelta(minutes=float(delta_custom.get()), microseconds=1)
        obj = speed_recorder.Main(
            url_listbox.get(0, tk.END), save_log.get(), headless.get())

        obj.add_recorder(Result2Display(tree))
        obj = common.AutoFlush(obj, timedelta(minutes=30))
        obj = common.Sequence(obj, delta)
        obj.start()


    def stop_button_clicked():
        nonlocal obj
        if obj is not None:
            obj.stop()
            obj = None


    def copy_selected_to_clipboard():
        nonlocal tree
        selected_items: tuple[str, ...] = tree.selection()
        if selected_items:
            selected_data = []
            for item in selected_items:
                row = tree.item(item)['values']
                selected_data.append(row)

            # 将选中的数据转换为制表符分隔的字符串
            clipboard_text = ""
            for row in selected_data:
                clipboard_text += "\t".join(map(str, row)) + "\n"

            # 复制到剪贴板
            root.clipboard_clear()
            root.clipboard_append(clipboard_text)
            root.update()  # 更新剪贴板内容

            print("选中的数据已复制到剪贴板")


    root = tk.Tk()
    root.title("定时测速")

    # 创建默认项列表
    tk.Label(root, text="测速网站").pack()
    url_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=8)
    for item in speedspider.URLS:
        url_listbox.insert(tk.END, item)
    url_listbox.pack()

    # 输入框和按钮
    edit_frame = ttk.Frame(root)
    add_url = tk.Entry(edit_frame, width=38)
    add_url.pack(side=tk.LEFT)
    add_button = tk.Button(edit_frame, text="添加", command=add_item)
    add_button.pack(side=tk.LEFT)
    delete_button = tk.Button(edit_frame, text="删除", command=delete_item)
    delete_button.pack(side=tk.LEFT)
    edit_frame.pack()


    save_log = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="保存结果到文件", variable=save_log).pack()
    headless = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="浏览器无头", variable=headless).pack()

    custom_frame = ttk.Frame(root)
    tk.Label(custom_frame, text="每隔").pack(side=tk.LEFT)
    delta_custom = tk.Entry(custom_frame, width=3)
    delta_custom.insert(0, "5")
    delta_custom.pack(side=tk.LEFT)
    tk.Label(custom_frame, text="分钟").pack(side=tk.LEFT)
    custom_frame.pack()

    edit_frame = ttk.Frame(root)
    start_button = tk.Button(edit_frame, text="开始", command=start_button_clicked)
    start_button.pack(side=tk.LEFT)
    stop_button = tk.Button(edit_frame, text="停止", command=stop_button_clicked)
    stop_button.pack(side=tk.RIGHT)
    edit_frame.pack()

    columns = ("延迟", "抖动", "上传", "下载")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill=tk.X)

    copy_button = tk.Button(root, text="复制选中到剪贴板", command=copy_selected_to_clipboard)
    copy_button.pack()

    obj = None

    root.mainloop()

if __name__ == "__main__":
    main()