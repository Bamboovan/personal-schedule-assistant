"""ANSI 终端彩色输出工具。

提供跨平台的彩色终端输出支持。

示例:
    >>> from src.ansi_utils import print_success, print_error, print_info
    >>> print_success("日程创建成功")
    >>> print_error("时间冲突")
"""
import os
import sys


class Colors:
    """ANSI 颜色代码。"""
    # 基础颜色
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

    # 重置
    END = '\033[0m'


def _supports_color() -> bool:
    """检测终端是否支持彩色输出。"""
    # 检查是否强制禁用颜色
    if os.environ.get('NO_COLOR'):
        return False

    # Windows 检测
    if sys.platform == 'win32':
        # Windows 10+ 支持 ANSI 颜色
        return True

    # Unix-like 系统
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        return True

    return False


_COLOR_ENABLED = _supports_color()


def colorize(text: str, color: str) -> str:
    """为文本添加颜色。

    Args:
        text: 要着色的文本
        color: ANSI 颜色代码

    Returns:
        着色后的文本（如果不支持颜色则返回原文本）
    """
    if _COLOR_ENABLED:
        return f"{color}{text}{Colors.END}"
    return text


def print_success(message: str) -> None:
    """打印成功消息（绿色）。"""
    if _COLOR_ENABLED:
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    else:
        print(f"[成功] {message}")


def print_error(message: str) -> None:
    """打印错误消息（红色）。"""
    if _COLOR_ENABLED:
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    else:
        print(f"[错误] {message}")


def print_warning(message: str) -> None:
    """打印警告消息（黄色）。"""
    if _COLOR_ENABLED:
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    else:
        print(f"[警告] {message}")


def print_info(message: str) -> None:
    """打印信息消息（蓝色）。"""
    if _COLOR_ENABLED:
        print(f"{Colors.BLUE}ℹ {message}{Colors.END}")
    else:
        print(f"[信息] {message}")


def print_conflict(message: str) -> None:
    """打印冲突消息（黄色加粗）。"""
    if _COLOR_ENABLED:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚡ {message}{Colors.END}")
    else:
        print(f"[冲突] {message}")


def format_event(title: str, start_time: str, end_time: str) -> str:
    """格式化日程显示。

    Args:
        title: 日程标题
        start_time: 开始时间
        end_time: 结束时间

    Returns:
        格式化后的日程字符串
    """
    if _COLOR_ENABLED:
        return f"{Colors.CYAN}{title}{Colors.END} ({start_time} - {end_time})"
    return f"{title} ({start_time} - {end_time})"