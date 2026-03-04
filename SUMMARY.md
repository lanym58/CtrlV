# 工作总结

## 项目背景

用户需要一个 Python 程序，能够从 Markdown 文件读取内容并模拟键盘录入到当前活动窗口，主要用于将文档内容输入到不支持粘贴操作的目标程序中。

## 需求分析

1. **Markdown 解析**：读取 .md 文件，移除格式符号，只保留纯文本
2. **键盘模拟**：模拟真实键盘输入，支持中文、空格、换行
3. **运行时控制**：支持暂停、继续、重新开始、调速等快捷键
4. **兼容性**：适用于不支持剪贴板粘贴的目标程序

## 技术方案演进

### 方案一：剪贴板粘贴法（已放弃）
- 使用 `pyperclip` 复制到剪贴板
- 使用 `pyautogui.hotkey('ctrl', 'v')` 粘贴
- **问题**：目标程序不支持粘贴操作

### 方案二：Windows 剪贴板 API（已放弃）
- 使用 `ctypes` 调用 Windows 剪贴板 API
- **问题**：出现内存访问错误（access violation）

### 方案三：PowerShell/clip 命令（已放弃）
- 使用 PowerShell 或 clip 命令操作剪贴板
- **问题**：仍然依赖剪贴板，目标程序不支持

### 方案四：Windows SendInput API（最终方案）
- 使用 `ctypes` 调用 Windows `SendInput` API
- 设置 `KEYEVENTF_UNICODE` 标志发送 Unicode 字符
- **优点**：真正的键盘模拟，不依赖剪贴板，支持所有 Unicode 字符

## 最终实现

### 核心代码

```python
def send_unicode_char(char):
    """使用 Windows SendInput API 发送 Unicode 字符"""
    inputs = (INPUT * 2)()

    # Key down
    inputs[0].type = INPUT_KEYBOARD
    inputs[0].ki.wVk = 0
    inputs[0].ki.wScan = ord(char)
    inputs[0].ki.dwFlags = KEYEVENTF_UNICODE

    # Key up
    inputs[1].type = INPUT_KEYBOARD
    inputs[1].ki.wScan = ord(char)
    inputs[1].ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP

    ctypes.windll.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))
```

### 依赖库

- `keyboard` - 全局热键监听

### 文件结构

```
CtrlV/
├── keyboard_typing.py    # 主程序
├── requirements.txt      # 依赖文件
├── README.md            # 使用说明
└── test.md              # 测试文件
```

## 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| Markdown 文件读取 | ✅ | UTF-8 编码 |
| 格式符号清理 | ✅ | 标题、加粗、链接等 |
| 中文输入 | ✅ | Unicode 字符支持 |
| 空格输入 | ✅ | - |
| 换行输入 | ✅ | - |
| 暂停/继续 | ✅ | F6 |
| 重新开始 | ✅ | F7 |
| 加快速度 | ✅ | F8 |
| 减慢速度 | ✅ | F9 |
| 停止退出 | ✅ | ESC |
| 进度显示 | ✅ | 行数和字符数 |

## 遇到的问题及解决

1. **中文输入失败**
   - 原因：剪贴板粘贴方式不被目标程序支持
   - 解决：改用 Windows SendInput API 直接发送 Unicode 键盘事件

2. **内存访问错误**
   - 原因：ctypes 调用剪贴板 API 参数配置错误
   - 解决：放弃剪贴板方案，使用 SendInput

3. **热键不响应**
   - 原因：keyboard 库需要管理员权限
   - 解决：文档说明需要管理员权限运行

## 使用说明

```bash
# 安装依赖
pip install keyboard

# 运行程序
python keyboard_typing.py 文件.md

# 自定义参数
python keyboard_typing.py 文件.md -d 0.02 --char-delay 0.01 -c 3
```

## 后续优化建议

1. 添加 GUI 界面
2. 支持更多 Markdown 格式（表格、脚注等）
3. 添加配置文件支持
4. 跨平台支持（macOS、Linux）
