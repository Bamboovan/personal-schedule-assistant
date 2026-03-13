"""日程解析模块。

从聊天记录和 Markdown 文档中提取日程信息。

提供功能：
- 解析 Markdown 文件中的日程
- 解析聊天记录中的日程
- 将各种时间格式标准化

示例:
    >>> from src.doc_parser import ScheduleParser
    >>> parser = ScheduleParser()
    >>> schedules = parser.parse_chat_log("明天下午3点开会")
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict


class TimeInfo(TypedDict):
    """时间信息结构。"""
    raw: str
    groups: tuple[str, ...]


class ScheduleInfo(TypedDict):
    """日程信息结构。"""
    title: str
    time_info: TimeInfo
    description: str
    source: str
    context: str


class ScheduleParser:
    """从聊天记录和 Markdown 文档中提取日程信息。"""

    # 中文时间段映射
    CHINESE_TIME_PERIODS: dict[str, tuple[int, int]] = {
        '凌晨': (0, 6),    # 0-6点
        '上午': (6, 12),   # 6-12点
        '中午': (11, 14),  # 11-14点
        '下午': (12, 18),  # 12-18点
        '晚上': (18, 24),  # 18-24点
    }

    # 时间模式匹配
    TIME_PATTERNS: list[str] = [
        # 中文时间范围：下午3点到5点
        r'(凌晨|上午|中午|下午|晚上)?\s*(\d{1,2})\s*点\s*(\d{1,2})?\s*(分|半)?\s*[到至~]\s*(\d{1,2})\s*点\s*(\d{1,2})?\s*(分|半)?',
        # 中文时间点：下午3点、下午3点半、下午3点15
        r'(凌晨|上午|中午|下午|晚上)?\s*(\d{1,2})\s*点\s*(\d{1,2})?\s*(分|半)?',
        # 完整日期范围：2026-03-10 15:00~16:00
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})?\s*[-~至到]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})?',
        # 完整日期 + 时间：2026-03-10 15:00
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})',
        # 月日范围：3 月 10 日 15:00~16:00
        r'(\d{1,2}月\d{1,2}日)\s*(\d{1,2}:\d{2})?\s*[-~至到]\s*(\d{1,2}月\d{1,2}日)\s*(\d{1,2}:\d{2})?',
        # 相对时间范围：明天 15:00~16:00
        r'(今天|明天|后天|下周一|下周二|下周三|下周四|下周五|下周六|下周日)*(\d{1,2}:\d{2})?\s*[-~至到]\s*(\d{1,2}:\d{2})?',
        # 相对时间 + 时间：明天 15:00
        r'(今天|明天|后天|下周一|下周二|下周三|下周四|下周五|下周六|下周日)*(\d{1,2}:\d{2})',
    ]

    def parse_markdown_file(self, file_path: str) -> list[ScheduleInfo]:
        """解析 Markdown 文件，提取日程信息。

        Args:
            file_path: Markdown 文件路径

        Returns:
            提取的日程信息列表
        """
        content = Path(file_path).read_text(encoding='utf-8')
        return self.extract_schedules(content, source=file_path)

    def parse_chat_log(self, chat_text: str) -> list[ScheduleInfo]:
        """解析聊天记录，提取日程信息。

        Args:
            chat_text: 聊天记录文本

        Returns:
            提取的日程信息列表
        """
        return self.extract_schedules(chat_text, source="chat")

    def extract_schedules(self, text: str, source: str = "") -> list[ScheduleInfo]:
        """从文本中提取日程信息。

        Args:
            text: 要解析的文本
            source: 来源标识

        Returns:
            提取的日程信息列表
        """
        schedules: list[ScheduleInfo] = []

        # 提取日程关键词
        schedule_keywords = ['会议', '日程', '安排', '约会', '活动', '面试', '汇报', '讨论', 'review']

        lines = text.split('\n')
        for i, line in enumerate(lines):
            # 检查是否包含日程相关关键词
            if any(keyword in line for keyword in schedule_keywords):
                schedule_info = self._parse_schedule_line(line, lines, i)
                if schedule_info:
                    schedule_info['source'] = source
                    schedules.append(schedule_info)

        return schedules

    def _parse_schedule_line(self, line: str, all_lines: list[str], current_idx: int) -> ScheduleInfo:
        """解析单行日程信息。

        Args:
            line: 当前行内容
            all_lines: 所有行内容
            current_idx: 当前行索引

        Returns:
            日程信息字典
        """
        schedule: ScheduleInfo = {
            'title': self._extract_title(line),
            'time_info': self._extract_time(line),
            'description': line.strip(),
            'source': '',
            'context': '',
        }

        # 尝试从上下文获取更多信息
        if current_idx > 0:
            schedule['context'] = all_lines[current_idx - 1].strip()

        return schedule

    def _extract_title(self, text: str) -> str:
        """提取日程标题。

        Args:
            text: 包含日程的文本

        Returns:
            提取的标题
        """
        # 移除时间信息，保留主题
        for pattern in self.TIME_PATTERNS:
            text = re.sub(pattern, '', text)

        # 移除相对日期词
        relative_date_pattern = r'(今天|明天|后天|下周一|下周二|下周三|下周四|下周五|下周六|下周日)\s*'
        text = re.sub(relative_date_pattern, '', text)

        # 清理文本
        text = re.sub(r'[：:]\s*$', '', text)
        text = re.sub(r'^[\s\-•*]+', '', text)

        return text.strip()[:50] if text.strip() else "未命名日程"

    def _extract_time(self, text: str) -> TimeInfo:
        """提取时间信息。

        Args:
            text: 包含时间的文本

        Returns:
            时间信息字典
        """
        for pattern in self.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return {
                    'raw': match.group(0),
                    'groups': match.groups()
                }
        return {'raw': '', 'groups': ()}

    def _parse_chinese_time(self, time_str: str) -> tuple[int, int] | None:
        """解析中文时间格式，返回 (小时, 分钟) 或 None。

        Args:
            time_str: 包含中文时间的字符串

        Returns:
            (小时, 分钟) 元组，或 None
        """
        # 匹配：时间段 + 数字 + 点 + 可选分/半（支持空格）
        match = re.search(
            r'(凌晨|上午|中午|下午|晚上)?\s*(\d{1,2})\s*点\s*(\d{1,2})?\s*(分|半)?',
            time_str
        )
        if not match:
            return None

        period, hour_str, minute_str, minute_unit = match.groups()
        hour = int(hour_str)

        # 处理分钟
        if minute_unit == '半':
            minute = 30
        elif minute_str:
            minute = int(minute_str)
        else:
            minute = 0

        # 根据时间段调整小时
        if period:
            if period == '下午' and hour < 12:
                hour += 12
            elif period == '晚上' and hour < 12:
                hour += 12
            elif period == '凌晨' and hour == 12:
                hour = 0
            # 上午、中午保持原样

        return (hour, minute)

    def normalize_time(self, time_str: str) -> str:
        """将各种时间格式标准化为 YYYY-MM-DD HH:MM。

        Args:
            time_str: 时间字符串

        Returns:
            标准化的时间字符串
        """
        # 处理相对时间
        today = datetime.now()

        relative_days: dict[str, int] = {
            '今天': 0,
            '明天': 1,
            '后天': 2,
            '下周一': (7 - today.weekday()) % 7 + 7,
            '下周二': (1 - today.weekday()) % 7 + 7,
            '下周三': (2 - today.weekday()) % 7 + 7,
            '下周四': (3 - today.weekday()) % 7 + 7,
            '下周五': (4 - today.weekday()) % 7 + 7,
            '下周六': (5 - today.weekday()) % 7 + 7,
            '下周日': (6 - today.weekday()) % 7 + 7,
        }

        for rel_str, days in relative_days.items():
            if rel_str in time_str:
                target_date = today + timedelta(days=days)
                # 先尝试中文时间格式
                chinese_time = self._parse_chinese_time(time_str)
                if chinese_time:
                    hour, minute = chinese_time
                    return f"{target_date.strftime('%Y-%m-%d')} {hour:02d}:{minute:02d}"
                # 再尝试 HH:MM 格式
                time_match = re.search(r'(\d{1,2}:\d{2})', time_str)
                if time_match:
                    return f"{target_date.strftime('%Y-%m-%d')} {time_match.group(1)}"
                else:
                    return f"{target_date.strftime('%Y-%m-%d')} 09:00"

        # 尝试中文时间格式（无相对日期）
        chinese_time = self._parse_chinese_time(time_str)
        if chinese_time:
            hour, minute = chinese_time
            return f"{hour:02d}:{minute:02d}"

        # 处理标准日期格式
        date_match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', time_str)
        if date_match:
            year, month, day = date_match.groups()
            time_match = re.search(r'(\d{1,2}:\d{2})', time_str)
            time = time_match.group(1) if time_match else "09:00"
            return f"{year}-{month.zfill(2)}-{day.zfill(2)} {time}"

        return time_str


# 使用示例
parser = ScheduleParser()
