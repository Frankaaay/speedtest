# 配置

## 环境配置

建议使用 Python 3.12+ 

虚拟环境参考[官网](https://docs.python.org/zh-cn/3/library/venv.html)

同时建议修改[PowerShell执行策略](https://learn.microsoft.com/zh-cn/powershell/module/microsoft.powershell.core/about/about_execution_policies)

## 打包

```sh
pyinstaller ./toolkit.py  -i ./flymodem.ico -y --noconsole -y && ./copy.ps1
```

在 `dist/toolkit` 文件夹中找到生成的可执行文件。

