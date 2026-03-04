# CtrlV - Markdown 键盘录入模拟器

从 Markdown 文件读取内容，模拟键盘逐字符输入到任意目标窗口，支持中文、空格、换行，并移除 Markdown 格式符号。

## 功能特点

- 支持 **中文** 及所有 Unicode 字符输入
- 自动移除 **Markdown 格式符号**（标题、加粗、链接等）
- **运行时快捷键控制**：暂停、继续、重新开始、调速
- 使用 Windows SendInput API，**真正的键盘模拟**（非剪贴板粘贴）
- 适用于不支持粘贴的目标程序

## 安装

```bash
pip install keyboard
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python keyboard_typing.py 文件.md
```

### 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--delay` | `-d` | 0.01 | 行间延迟（秒） |
| `--char-delay` | 无 | 0.005 | 字符间延迟（秒） |
| `--countdown` | `-c` | 5 | 开始前倒计时（秒） |

### 示例

```bash
# 使用默认参数
python keyboard_typing.py test.md

# 自定义延迟和倒计时
python keyboard_typing.py test.md -d 0.02 --char-delay 0.01 -c 3
```

## 快捷键控制

| 快捷键 | 功能 |
|--------|------|
| `F6` | 暂停 / 继续 |
| `F7` | 重新开始输入 |
| `F8` | 加快输入速度 |
| `F9` | 减慢输入速度 |
| `ESC` | 停止并退出 |

## Markdown 格式清理

程序自动移除以下 Markdown 格式符号：

| 格式 | 原文 | 清理后 |
|------|------|--------|
| 标题 | `# 标题` | 标题 |
| 加粗 | `**文本**` | 文本 |
| 斜体 | `*文本*` | 文本 |
| 代码 | `` `代码` `` | 代码 |
| 链接 | `[文字](url)` | 文字 |
| 引用 | `> 引用` | 引用 |
| 列表 | `- 项目` | 项目 |

## 使用步骤

1. 准备 Markdown 文件（如 `content.md`）
2. 运行程序：`python keyboard_typing.py content.md`
3. 在 **5 秒倒计时内** 切换到目标窗口（记事本、Word、浏览器等）
4. 程序自动开始输入
5. 使用快捷键控制输入过程

## 注意事项

1. **管理员权限**：`keyboard` 库监听全局热键可能需要管理员权限
2. **输入焦点**：确保倒计时结束前目标窗口已获得焦点
3. **输入速度**：如果目标程序响应慢，可增加 `--char-delay` 参数

## 技术实现

- 使用 Windows `SendInput` API 发送 Unicode 键盘事件
- `KEYEVENTF_UNICODE` 标志支持任意 Unicode 字符
- `keyboard` 库实现全局热键监听

## 文件结构

```
CtrlV/
├── keyboard_typing.py    # 主程序
├── requirements.txt      # 依赖文件
├── README.md            # 使用说明
└── test.md              # 测试文件
```

## License

MIT License
