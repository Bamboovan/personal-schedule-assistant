"""日程管理核心模块。

基于 NexAU 框架实现的个人日程助手。

提供功能：
- 日程的增删改查操作
- JSON 文件持久化存储
- 时间格式验证

示例:
    >>> from src.event_manager import EventManager
    >>> manager = EventManager()
    >>> result = manager.add_event("会议", "2026-03-15 10:00", "2026-03-15 11:00")
"""
import fcntl
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, TypedDict, Unpack


class EventDict(TypedDict):
    """日程数据结构。"""
    event_id: str
    title: str
    start_time: str
    end_time: str
    description: str
    location: str
    reminder: int
    created_at: str


class EventError(Exception):
    """日程操作错误基类。"""
    pass


class EventNotFoundError(EventError):
    """日程不存在。"""
    def __init__(self, event_id: str) -> None:
        self.event_id = event_id
        super().__init__(f"未找到日程 ID: {event_id}")


class InvalidTimeFormatError(EventError):
    """时间格式无效。"""
    def __init__(self, time_str: str) -> None:
        self.time_str = time_str
        super().__init__(f"时间格式无效: {time_str}")


class InvalidTimeRangeError(EventError):
    """时间范围无效。"""
    def __init__(self, start_time: str, end_time: str) -> None:
        self.start_time = start_time
        self.end_time = end_time
        super().__init__(f"结束时间必须晚于开始时间: {start_time} -> {end_time}")


def _validate_time_format(time_str: str) -> bool:
    """验证时间格式是否为 YYYY-MM-DD HH:MM。"""
    try:
        datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def _validate_time_range(start_time: str, end_time: str) -> bool:
    """验证时间范围是否有效（结束时间晚于开始时间）。"""
    try:
        start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        return end > start
    except ValueError:
        return False


class EventManager:
    """日程管理器，提供日程的增删改查操作。"""

    def __init__(self, data_file: str = "data/events.json") -> None:
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.events: dict[str, EventDict] = self._load_events()

    def _load_events(self) -> dict[str, EventDict]:
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data: dict[str, EventDict] = json.load(f)
                return data
        return {}

    def _save_events(self) -> None:
        with open(self.data_file, 'w', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(self.events, f, ensure_ascii=False, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def add_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: str = "",
        location: str = "",
        reminder: int = 15
    ) -> dict[str, str]:
        # 验证时间格式
        if not _validate_time_format(start_time):
            return {"status": "error", "message": f"开始时间格式无效: {start_time}"}
        if not _validate_time_format(end_time):
            return {"status": "error", "message": f"结束时间格式无效: {end_time}"}

        # 验证时间范围
        if not _validate_time_range(start_time, end_time):
            return {"status": "error", "message": "结束时间必须晚于开始时间"}

        import uuid
        event_id = str(uuid.uuid4())[:8]
        event: EventDict = {
            "event_id": event_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "location": location,
            "reminder": reminder,
            "created_at": datetime.now().isoformat()
        }
        self.events[event_id] = event
        self._save_events()
        return {"status": "success", "event_id": event_id, "message": f"已创建日程：{title}"}

    def modify_event(self, event_id: str, **kwargs: str | int) -> dict[str, str]:
        if event_id not in self.events:
            return {"status": "error", "message": f"未找到日程 ID: {event_id}"}

        event = self.events[event_id]
        for key, value in kwargs.items():
            if value and key in event:
                event[key] = value  # type: ignore[typeddict-item]

        # 如果修改了时间，验证时间范围
        start_time = event.get("start_time", "")
        end_time = event.get("end_time", "")
        if start_time and end_time and not _validate_time_range(start_time, end_time):
            return {"status": "error", "message": "结束时间必须晚于开始时间"}

        self._save_events()
        return {"status": "success", "message": f"已更新日程：{event['title']}"}

    def query_events(self, start_date: str, end_date: str, keyword: str = "") -> dict[str, str | int | list[EventDict]]:
        results: list[EventDict] = []
        for event in self.events.values():
            event_date = event['start_time'][:10]
            if start_date <= event_date <= end_date:
                if not keyword or keyword.lower() in event['title'].lower() or keyword in event['description']:
                    results.append(event)

        results.sort(key=lambda x: x['start_time'])
        return {"status": "success", "count": len(results), "events": results}

    def delete_event(self, event_id: str) -> dict[str, str]:
        if event_id not in self.events:
            return {"status": "error", "message": f"未找到日程 ID: {event_id}"}

        title = self.events[event_id]['title']
        del self.events[event_id]
        self._save_events()
        return {"status": "success", "message": f"已删除日程：{title}"}

    def check_conflict(
        self,
        start_time: str,
        end_time: str,
        exclude_event_id: Optional[str] = None
    ) -> list[EventDict]:
        """检查指定时间段是否有日程冲突。

        Args:
            start_time: 开始时间，格式 YYYY-MM-DD HH:MM
            end_time: 结束时间，格式 YYYY-MM-DD HH:MM
            exclude_event_id: 排除的日程 ID（用于修改时排除自身）

        Returns:
            与指定时间段冲突的日程列表
        """
        conflicts: list[EventDict] = []
        try:
            new_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            new_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return conflicts

        for event in self.events.values():
            if exclude_event_id and event["event_id"] == exclude_event_id:
                continue

            try:
                event_start = datetime.strptime(event["start_time"], "%Y-%m-%d %H:%M")
                event_end = datetime.strptime(event["end_time"], "%Y-%m-%d %H:%M")

                # 检查时间重叠
                if new_start < event_end and new_end > event_start:
                    conflicts.append(event)
            except ValueError:
                continue

        return conflicts


# 绑定函数（供 Tool.from_yaml 使用）
event_manager = EventManager()


def add_event_binding(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    reminder: int = 15
) -> dict[str, str]:
    return event_manager.add_event(title, start_time, end_time, description, location, reminder)


def modify_event_binding(event_id: str, **kwargs: str | int) -> dict[str, str]:
    return event_manager.modify_event(event_id, **kwargs)


def query_event_binding(start_date: str, end_date: str, keyword: str = "") -> dict[str, str | int | list[EventDict]]:
    return event_manager.query_events(start_date, end_date, keyword)


def delete_event_binding(event_id: str) -> dict[str, str]:
    return event_manager.delete_event(event_id)


def parse_document_binding(content: str, source_type: str) -> dict[str, str]:
    """从文档中提取日程信息。

    Args:
        content: 文档内容或文件路径
        source_type: 内容类型，'file' 或 'text'

    Returns:
        提取结果，包含日程列表
    """
    from src.doc_parser import ScheduleParser

    parser = ScheduleParser()
    try:
        if source_type == "file":
            schedules = parser.parse_markdown_file(content)
        else:
            schedules = parser.parse_chat_log(content)

        # 标准化时间
        for schedule in schedules:
            if schedule.get("time_info", {}).get("raw"):
                schedule["normalized_time"] = parser.normalize_time(
                    schedule["time_info"]["raw"]
                )

        return {
            "status": "success",
            "count": len(schedules),
            "schedules": schedules,
            "message": f"已从文档中提取 {len(schedules)} 条日程信息"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"解析文档失败: {str(e)}"
        }
