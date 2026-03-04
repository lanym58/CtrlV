import re
import time
import keyboard
import argparse
import sys
import ctypes
from ctypes import wintypes

# Windows API 常量
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_RETURN = 0x0D

# Windows API 结构体
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("ki", KEYBDINPUT),
        ("padding", ctypes.c_ubyte * 8)
    ]

def send_unicode_char(char):
    """发送单个 Unicode 字符"""
    inputs = (INPUT * 2)()

    # Key down
    inputs[0].type = INPUT_KEYBOARD
    inputs[0].ki.wVk = 0
    inputs[0].ki.wScan = ord(char)
    inputs[0].ki.dwFlags = KEYEVENTF_UNICODE
    inputs[0].ki.time = 0
    inputs[0].ki.dwExtraInfo = None

    # Key up
    inputs[1].type = INPUT_KEYBOARD
    inputs[1].ki.wVk = 0
    inputs[1].ki.wScan = ord(char)
    inputs[1].ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
    inputs[1].ki.time = 0
    inputs[1].ki.dwExtraInfo = None

    ctypes.windll.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))

def send_enter():
    """发送回车键"""
    keyboard.press_and_release('enter')

def type_string(text, delay=0.01):
    """逐字符输入文本"""
    for char in text:
        send_unicode_char(char)
        time.sleep(delay)

class MarkdownTyping:
    def __init__(self, delay=0.01, char_delay=0.005):
        self.delay = delay
        self.char_delay = char_delay
        self.paused = False
        self.restart = False
        self.stop = False
        self.original_text = ""

    def clean_markdown(self, text):
        """移除Markdown格式符号"""
        # 代码块
        text = re.sub(r'```\w*\n?', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # 标题
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # 加粗/斜体
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        # 链接和图片
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 引用
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        # 列表
        text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        # 分隔线
        text = re.sub(r'^[-]{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[*]{3,}$', '', text, flags=re.MULTILINE)

        return text.strip()

    def read_file(self, file_path):
        """读取Markdown文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def setup_hotkeys(self):
        """设置全局快捷键"""
        keyboard.add_hotkey('f6', self.toggle_pause)
        keyboard.add_hotkey('f7', self.do_restart)
        keyboard.add_hotkey('f8', self.speed_up)
        keyboard.add_hotkey('f9', self.slow_down)
        keyboard.add_hotkey('esc', self.do_stop)

    def toggle_pause(self):
        self.paused = not self.paused
        status = "已暂停" if self.paused else "继续输入"
        print(f"[状态] {status}")

    def do_restart(self):
        self.restart = True
        self.paused = False
        print("[状态] 重新开始输入")

    def speed_up(self):
        self.char_delay = max(0.001, self.char_delay - 0.002)
        print(f"[状态] 速度加快，字符延迟: {self.char_delay:.3f}s")

    def slow_down(self):
        self.char_delay = min(0.1, self.char_delay + 0.002)
        print(f"[状态] 速度减慢，字符延迟: {self.char_delay:.3f}s")

    def do_stop(self):
        self.stop = True
        print("[状态] 停止输入")

    def type_text(self, text):
        """模拟键盘录入"""
        lines = text.split('\n')
        print(f"共 {len(lines)} 行，{len(text)} 字符待输入")

        char_count = 0
        for i, line in enumerate(lines):
            if self.stop:
                break

            if self.restart:
                self.restart = False
                return False

            while self.paused and not self.stop and not self.restart:
                time.sleep(0.1)

            if self.stop or self.restart:
                if self.restart:
                    self.restart = False
                    return False
                break

            # 逐字符输入
            for char in line:
                if self.stop:
                    break
                while self.paused and not self.stop:
                    time.sleep(0.1)
                if self.stop:
                    break

                send_unicode_char(char)
                char_count += 1
                time.sleep(self.char_delay)

            # 输入回车（最后一行除外）
            if i < len(lines) - 1 and not self.stop:
                send_enter()
                time.sleep(self.delay)

            # 显示进度
            print(f"已输入第 {i+1}/{len(lines)} 行 ({char_count} 字符)", end='\r')

        print()
        return True

    def run(self, file_path, countdown=5):
        """主运行函数"""
        raw_text = self.read_file(file_path)
        self.original_text = self.clean_markdown(raw_text)

        print(f"原文长度: {len(raw_text)} 字符")
        print(f"清理后长度: {len(self.original_text)} 字符")

        self.setup_hotkeys()

        print("\n快捷键说明:")
        print("  F6  - 暂停/继续")
        print("  F7  - 重新开始")
        print("  F8  - 加快速度")
        print("  F9  - 减慢速度")
        print("  ESC - 停止退出")

        print(f"\n将在 {countdown} 秒后开始，请切换到目标窗口...")
        for i in range(countdown, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        while True:
            self.stop = False
            self.restart = False
            print("\n开始输入...")
            completed = self.type_text(self.original_text)
            if completed:
                break
            if self.stop:
                break
            print("重新开始...")

        keyboard.unhook_all()
        print("程序结束")

def main():
    parser = argparse.ArgumentParser(description='从MD文件读取内容并模拟键盘录入')
    parser.add_argument('file', help='Markdown文件路径')
    parser.add_argument('--delay', '-d', type=float, default=0.01, help='行间延迟(秒)')
    parser.add_argument('--char-delay', type=float, default=0.005, help='字符间延迟(秒)')
    parser.add_argument('--countdown', '-c', type=int, default=5, help='开始前倒计时(秒)')

    args = parser.parse_args()

    try:
        typer = MarkdownTyping(delay=args.delay, char_delay=args.char_delay)
        typer.run(args.file, args.countdown)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.file}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
