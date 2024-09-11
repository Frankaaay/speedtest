
## 激活虚拟环境

```ps1
./Scripts/Activate.ps1
```

## 打包

```sh
pyinstaller ./toolkit.py  -i ./flymodem.ico -y
```

在 `dist/toolkit` 文件夹中找到生成的可执行文件。

将`empty_ping/` `empty_speed/` `multi3.exe` `flymodem.png`拷贝到可执行文件同一目录下。