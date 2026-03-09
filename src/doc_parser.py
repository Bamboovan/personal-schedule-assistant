import re
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path

class ScheduleParser:
    """从聊天记录和 Markdown 文档中提取日程信息"""

    # 时间模式匹配
    TIME_PATTERNS = [
        # 完整日期范围：2026-03-10 15:00~16:00
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})?\s*[-~至到]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})?',
        # 完整日期 + 时间：2026-03-10 15:00
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})',
        # 月日范围：3 月 10 日 15:00~16:00
        r'(\d{1,2}月\d{1,2}日)\s*(\d{1,2}:\d{2})?\s*[-~至到]\s*(\d{1,2}月\d{1,2}日)\s*(\d{1,2}:\d{2})?',
        # 相对时间范围：明天 15:00~16:00
        r'(今天 | 明天 | 后天 | 下周一 | 下周二 | 下周三 | 下周四 | 下周五 | 下周六 | 下周日)*(\d{1,2}:\d{2})?\s*[-~至到]\s*(\d{1,2}:\d{2})?',
        # 相对时间 + 时间：明天 15:00
        r'(今天 | 明天 | 后天 | 下周一 | 下周二 | 下周三 | 下周四 | 下周五 | 下周六 | 下周日)*(\d{1,2}:\d{2})',
    ]

    def parse_markdown_file(self, file_path: str) -> List[Dict]:
        """解析 Markdown 文件，提取日程信息"""
        content = Path(file_path).read_text(encoding='utf-8')
        return self.extract_schedules(content, source=file_path)

    def parse_chat_log(self, chat_text: str) -> List[Dict]:
        """解析聊天记录，提取日程信息"""
        return self.extract_schedules(chat_text, source="chat")

    def extract_schedules(self, text: str, source: str = "") -> List[Dict]:
        """从文本中提取日程信息"""
        schedules = []

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

    def _parse_schedule_line(self, line: str, all_lines: List[str], current_idx: int) -> Dict:
        """解析单行日程信息"""
        schedule = {
            'title': self._extract_title(line),
            'time_info': self._extract_time(line),
            'description': line.strip(),
        }

        # 尝试从上下文获取更多信息
        if current_idx > 0:
            schedule['context'] = all_lines[current_idx - 1].strip()

        return schedule

    def _extract_title(self, text: str) -> str:
        """提取日程标题"""
        # 移除时间信息，保留主题
        for pattern in self.TIME_PATTERNS:
            text = re.sub(pattern, '', text)

        # 清理文本
        text = re.sub(r'[：:]\s*$', '', text)
        text = re.sub(r'^[\s\-•*]+', '', text)

        return text.strip()[:50] if text.strip() else "未命名日程"

    def _extract_time(self, text: str) -> Dict:
        """提取时间信息"""
        for pattern in self.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return {
                    'raw': match.group(0),
                    'groups': match.groups()
                }
        return {'raw': '', 'groups': ()}

    def normalize_time(self, time_str: str) -> str:
        """将各种时间格式标准化为 YYYY-MM-DD HH:MM"""
        # 处理相对时间
        today = datetime.now()
        
        relative_days = {
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
                # 提取时间
                time_match = re.search(r'(\d{1,2}:\d{2})', time_str)
                if time_match:
                    return f"{target_date.strftime('%Y-%m-%d')} {time_match.group(1)}"
                else:
                    return f"{target_date.strftime('%Y-%m-%d')} 09:00"

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
