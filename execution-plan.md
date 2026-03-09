# 个人日程助手智能体 - 执行计划

## 📋 项目概述

基于 **NexAU** 框架构建一个个人日程助手智能体，能够从聊天记录和飞书文档/Markdown 笔记中自动创建、修改日程。

---

## 🎯 目标拆解

| 目标 | 说明 |
|------|------|
| 搭建智能体框架 | 使用 NexAU v0.3.9 |
| 设计日程工具 | 添加日程、修改日程、查询日程、删除日程 |
| 集成文档解析 | 从 Markdown/飞书文档中提取日程信息 |
| 支持多模型 | Qwen / DeepSeek / 硅基流动 API |

---

## 📁 项目结构

```
personal-assistant/
├── .env                    # 环境变量配置
├── config.yaml             # 智能体配置文件
├── main.py                 # 启动脚本
├── tools/                  # 工具定义目录
│   ├── add_event.tool.yaml
│   ├── modify_event.tool.yaml
│   ├── query_event.tool.yaml
│   └── delete_event.tool.yaml
├── skills/                 # 技能目录（可选）
│   └── schedule-skill/
├── src/                    # 工具实现
│   ├── __init__.py
│   ├── event_manager.py    # 日程管理核心逻辑
│   └── doc_parser.py       # 文档解析器
├── data/                   # 数据存储
│   └── events.json         # 日程存储文件
├── logs/                   # 日志目录
└── docs/                   # 文档
    └── user-guide.md
```

---

## 📅 执行阶段

### 阶段一：环境搭建（预计 1-2 小时）

#### 1.1 安装 NexAU 框架

```bash
# 方式一：从 GitHub Release 安装（推荐）
pip install git+ssh://git@github.com/nex-agi/NexAU.git@v0.3.9

# 或使用 uv
uv pip install git+ssh://git@github.com/nex-agi/NexAU.git@v0.3.9
```

#### 1.2 创建项目结构

```bash
mkdir -p personal-assistant/{tools,skills,src,data,logs,docs}
cd personal-assistant
touch .env config.yaml main.py
touch src/{__init__.py,event_manager.py,doc_parser.py}
```

#### 1.3 配置环境变量

创建 `.env` 文件：

```bash
# LLM 配置（三选一）
# 方案 A: Qwen 系列（推荐，性价比高）
LLM_MODEL="qwen-plus"
LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_API_KEY="your-dashscope-api-key"

# 方案 B: DeepSeek
# LLM_MODEL="deepseek-chat"
# LLM_BASE_URL="https://api.deepseek.com/v1"
# LLM_API_KEY="your-deepseek-api-key"

# 方案 C: 硅基流动
# LLM_MODEL="your-model"
# LLM_BASE_URL="https://api.siliconflow.cn/v1"
# LLM_API_KEY="your-siliconflow-api-key"

# Langfuse 可观测性（可选）
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_HOST="https://us.cloud.langfuse.com"
```

---

### 阶段二：工具设计与实现（预计 3-4 小时）

#### 2.1 定义工具 YAML（工具描述层）

**`tools/add_event.tool.yaml`**
```yaml
name: add_event
description: 添加新的日程安排。从用户的聊天记录或文档中提取时间、标题、描述等信息创建日程。
parameters:
  type: object
  properties:
    title:
      type: string
      description: 日程标题
    start_time:
      type: string
      description: 开始时间，格式：YYYY-MM-DD HH:MM
    end_time:
      type: string
      description: 结束时间，格式：YYYY-MM-DD HH:MM
    description:
      type: string
      description: 日程详细描述
    location:
      type: string
      description: 日程地点（可选）
    reminder:
      type: integer
      description: 提前提醒时间（分钟），默认 15
  required:
    - title
    - start_time
    - end_time
```

**`tools/modify_event.tool.yaml`**
```yaml
name: modify_event
description: 修改现有日程。可以更改时间、标题、描述等信息。
parameters:
  type: object
  properties:
    event_id:
      type: string
      description: 日程 ID
    title:
      type: string
      description: 新标题（可选，不修改则留空）
    start_time:
      type: string
      description: 新开始时间（可选）
    end_time:
      type: string
      description: 新结束时间（可选）
    description:
      type: string
      description: 新描述（可选）
    location:
      type: string
      description: 新地点（可选）
  required:
    - event_id
```

**`tools/query_event.tool.yaml`**
```yaml
name: query_event
description: 查询日程。可以按日期范围、关键词等条件搜索。
parameters:
  type: object
  properties:
    start_date:
      type: string
      description: 查询开始日期 YYYY-MM-DD
    end_date:
      type: string
      description: 查询结束日期 YYYY-MM-DD
    keyword:
      type: string
      description: 搜索关键词（可选）
  required:
    - start_date
    - end_date
```

**`tools/delete_event.tool.yaml`**
```yaml
name: delete_event
description: 删除日程
parameters:
  type: object
  properties:
    event_id:
      type: string
      description: 要删除的日程 ID
  required:
    - event_id
```

#### 2.2 实现工具逻辑（Python 实现层）

**`src/event_manager.py`**
```python
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
```

---

### 阶段三：文档解析器实现（预计 2-3 小时）

#### 3.1 创建文档解析技能

**`src/doc_parser.py`**
```python
import re
from datetime import datetime
from typing import List, Dict
from pathlib import Path

class ScheduleParser:
    """从聊天记录和 Markdown 文档中提取日程信息"""
    
    # 时间模式匹配
    TIME_PATTERNS = [
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})?[-~至到](\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(\d{1,2}:\d{2})?',
        r'(\d{1,2}月\d{1,2}日)\s*(\d{1,2}:\d{2})?[-~至到](\d{1,2}月\d{1,2}日)\s*(\d{1,2}:\d{2})?',
        r'(今天 | 明天 | 后天 | 下周一 | 下周二 | 下周三 | 下周四 | 下周五 | 下周六 | 下周日)\s*(\d{1,2}:\d{2})?[-~至到](\d{1,2}:\d{2})?',
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
        # TODO: 实现相对时间（今天、明天等）的转换
        return time_str

# 使用示例
parser = ScheduleParser()
```

---

### 阶段四：智能体配置与集成（预计 1-2 小时）

#### 4.1 创建系统提示词

**`system-prompt.md`**
```markdown
# 角色
你是一个专业的个人日程助手，帮助用户从聊天记录、笔记文档中创建和管理日程。

# 能力
1. 从用户的聊天描述中识别日程信息
2. 从 Markdown/飞书文档中提取日程安排
3. 使用工具创建、修改、查询、删除日程
4. 支持自然语言时间表达（如"明天下午 3 点"）

# 工作流程
1. 理解用户意图：是要创建、修改、查询还是删除日程
2. 提取关键信息：时间、标题、描述、地点等
3. 调用相应工具执行操作
4. 确认操作结果并反馈给用户

# 注意事项
- 时间格式统一为 YYYY-MM-DD HH:MM
- 创建日程时必须确认开始时间和结束时间
- 修改日程时需要先查询获取 event_id
- 删除操作前需要用户确认
```

#### 4.2 创建配置文件

**`config.yaml`**
```yaml
agent:
  name: personal-schedule-assistant
  max_context_tokens: 100000
  system_prompt: system-prompt.md
  system_prompt_type: jinja
  tool_call_mode: openai

llm:
  temperature: 0.7
  max_tokens: 4096
  model: ${LLM_MODEL}
  base_url: ${LLM_BASE_URL}
  api_key: ${LLM_API_KEY}
  api_type: openai_chat_completion

tools:
  - path: tools/add_event.tool.yaml
    binding: src.event_manager.add_event_binding
  - path: tools/modify_event.tool.yaml
    binding: src.event_manager.modify_event_binding
  - path: tools/query_event.tool.yaml
    binding: src.event_manager.query_event_binding
  - path: tools/delete_event.tool.yaml
    binding: src.event_manager.delete_event_binding

skills:
  - path: skills/schedule-skill

middleware:
  - logging

tracer:
  type: langfuse
  public_key: ${LANGFUSE_PUBLIC_KEY}
  secret_key: ${LANGFUSE_SECRET_KEY}
  host: ${LANGFUSE_HOST}
```

#### 4.3 创建启动脚本

**`main.py`**
```python
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from nexau import Agent, AgentConfig, LLMConfig, Tool
from nexau.archs.main_sub.execution.hooks import LoggingMiddleware

# 加载环境变量
load_dotenv()

logging.basicConfig(level=logging.INFO)

base_dir = Path(__file__).parent

# 导入工具绑定
from src.event_manager import (
    add_event_binding,
    modify_event_binding,
    query_event_binding,
    delete_event_binding,
)

# 配置工具
tools = [
    Tool.from_yaml(base_dir / "tools/add_event.tool.yaml", binding=add_event_binding),
    Tool.from_yaml(base_dir / "tools/modify_event.tool.yaml", binding=modify_event_binding),
    Tool.from_yaml(base_dir / "tools/query_event.tool.yaml", binding=query_event_binding),
    Tool.from_yaml(base_dir / "tools/delete_event.tool.yaml", binding=delete_event_binding),
]

# 配置 LLM
llm_config = LLMConfig(
    temperature=0.7,
    max_tokens=4096,
    model=os.getenv("LLM_MODEL"),
    base_url=os.getenv("LLM_BASE_URL"),
    api_key=os.getenv("LLM_API_KEY"),
    api_type="openai_chat_completion",
)

# 配置代理
agent_config = AgentConfig(
    name="personal-schedule-assistant",
    max_context_tokens=100000,
    system_prompt=(base_dir / "system-prompt.md").read_text(encoding='utf-8'),
    system_prompt_type="jinja",
    tool_call_mode="openai",
    llm_config=llm_config,
    tools=tools,
    middlewares=[
        LoggingMiddleware(
            model_logger="schedule-assistant",
            tool_logger="schedule-assistant",
            log_model_calls=True,
        ),
    ],
)

agent = Agent(config=agent_config)

if __name__ == "__main__":
    print("🤖 个人日程助手已启动！")
    print("示例命令：")
    print("  - '明天下午 3 点到 4 点有个团队会议，帮我创建日程'")
    print("  - '查询本周的所有日程'")
    print("  - '把周一下午的会议改到周三'")
    print("输入 'quit' 退出\n")
    
    while True:
        user_input = input("👤 你：")
        if user_input.lower() in ['quit', 'exit', '退出']:
            break
        
        response = agent.run(user_input)
        print(f"🤖 助手：{response}\n")
```

---

### 阶段五：测试与优化（预计 2-3 小时）

#### 5.1 测试用例

```python
# tests/test_schedule_assistant.py

def test_add_event():
    """测试添加日程"""
    result = add_event_binding(
        title="团队周会",
        start_time="2026-03-10 15:00",
        end_time="2026-03-10 16:00",
        description="讨论 Q2 计划",
        location="会议室 A"
    )
    assert result["status"] == "success"

def test_query_events():
    """测试查询日程"""
    result = query_event_binding(
        start_date="2026-03-01",
        end_date="2026-03-31"
    )
    assert result["status"] == "success"
    assert "events" in result

def test_modify_event():
    """测试修改日程"""
    # 先添加
    add_result = add_event_binding("测试会议", "2026-03-15 10:00", "2026-03-15 11:00")
    event_id = add_result["event_id"]
    
    # 再修改
    modify_result = modify_event_binding(
        event_id=event_id,
        title="修改后的会议"
    )
    assert modify_result["status"] == "success"

def test_delete_event():
    """测试删除日程"""
    add_result = add_event_binding("临时会议", "2026-03-20 14:00", "2026-03-20 15:00")
    event_id = add_result["event_id"]
    
    delete_result = delete_event_binding(event_id=event_id)
    assert delete_result["status"] == "success"
```

#### 5.2 集成测试场景

| 场景 | 输入 | 预期输出 |
|------|------|----------|
| 创建日程 | "明天下午 3 点开会" | 成功创建，返回 event_id |
| 查询日程 | "这周有什么安排" | 返回本周所有日程列表 |
| 修改日程 | "把周会的会议改到 4 点" | 成功修改时间 |
| 删除日程 | "取消明天的会议" | 成功删除 |
| 文档解析 | 上传 Markdown 笔记 | 提取所有日程并创建 |

---

## ✅ 验收标准

| 功能 | 验收标准 |
|------|----------|
| 工具调用 | 智能体能正确调用 4 个日程工具 |
| 时间理解 | 支持多种时间表达格式 |
| 文档解析 | 能从 Markdown 提取日程 |
| 持久化 | 日程数据保存到 JSON 文件 |
| 错误处理 | 无效输入有友好提示 |

---

## 📚 参考资源

- **NexAU 官方文档**: https://github.com/nex-agi/NexAU
- **NexAU 示例代码**: https://github.com/nex-agi/NexAU/tree/main/examples
- **DashScope API 文档**: https://help.aliyun.com/zh/dashscope
- **DeepSeek API 文档**: https://platform.deepseek.com/api-docs

---

## 🔄 后续扩展

1. **日历集成** - 对接 Google Calendar / 飞书日历
2. **提醒功能** - 邮件/短信/微信提醒
3. **冲突检测** - 自动检测时间冲突
4. **自然语言增强** - 支持更复杂的时间表达
5. **多用户支持** - 团队协作日程管理

---

**文档版本**: v1.0  
**创建时间**: 2026-03-09  
**预计总工时**: 9-14 小时
