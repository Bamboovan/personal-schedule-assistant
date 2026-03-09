import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
import uuid

@dataclass
class Event:
    event_id: str
    title: str
    start_time: str
    end_time: str
    description: str = ""
    location: str = ""
    reminder: int = 15
    created_at: str = ""

class EventManager:
    def __init__(self, data_file: str = "data/events.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.events = self._load_events()

    def _load_events(self) -> dict:
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_events(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def add_event(self, title: str, start_time: str, end_time: str,
                  description: str = "", location: str = "", reminder: int = 15) -> dict:
        event_id = str(uuid.uuid4())[:8]
        event = Event(
            event_id=event_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            reminder=reminder,
            created_at=datetime.now().isoformat()
        )
        self.events[event_id] = asdict(event)
        self._save_events()
        return {"status": "success", "event_id": event_id, "message": f"已创建日程：{title}"}

    def modify_event(self, event_id: str, **kwargs) -> dict:
        if event_id not in self.events:
            return {"status": "error", "message": f"未找到日程 ID: {event_id}"}

        event = self.events[event_id]
        for key, value in kwargs.items():
            if value and key in event:
                event[key] = value

        self._save_events()
        return {"status": "success", "message": f"已更新日程：{event['title']}"}

    def query_events(self, start_date: str, end_date: str, keyword: str = "") -> dict:
        results = []
        for event in self.events.values():
            event_date = event['start_time'][:10]
            if start_date <= event_date <= end_date:
                if not keyword or keyword.lower() in event['title'].lower() or keyword in event['description']:
                    results.append(event)

        results.sort(key=lambda x: x['start_time'])
        return {"status": "success", "count": len(results), "events": results}

    def delete_event(self, event_id: str) -> dict:
        if event_id not in self.events:
            return {"status": "error", "message": f"未找到日程 ID: {event_id}"}

        title = self.events[event_id]['title']
        del self.events[event_id]
        self._save_events()
        return {"status": "success", "message": f"已删除日程：{title}"}

# 绑定函数（供 Tool.from_yaml 使用）
event_manager = EventManager()

def add_event_binding(title: str, start_time: str, end_time: str,
                      description: str = "", location: str = "", reminder: int = 15) -> dict:
    return event_manager.add_event(title, start_time, end_time, description, location, reminder)

def modify_event_binding(event_id: str, **kwargs) -> dict:
    return event_manager.modify_event(event_id, **kwargs)

def query_event_binding(start_date: str, end_date: str, keyword: str = "") -> dict:
    return event_manager.query_events(start_date, end_date, keyword)

def delete_event_binding(event_id: str) -> dict:
    return event_manager.delete_event(event_id)
