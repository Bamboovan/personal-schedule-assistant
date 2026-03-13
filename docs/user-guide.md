# 个人日程助手 - 用户指南

## 📖 简介

个人日程助手是一个基于 NexAU 框架的智能体，能够从聊天记录和文档中自动创建、修改、查询和删除日程。

## 🚀 快速开始

### 1. 环境准备

使用 uv（推荐）：
```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

或使用 pip：
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，选择一种 LLM 配置：

```bash
# Qwen 系列（推荐）
LLM_MODEL="qwen-plus"
LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_API_KEY="your-dashscope-api-key"
```

### 3. 启动智能体

```bash
source .venv/bin/activate
python main.py
```

## 💡 使用示例

### 创建日程

```
👤 你：明天下午 3 点到 4 点有个团队会议，帮我创建日程
🤖 助手：已创建日程：团队会议 (event_id: abc12345)
```

### 查询日程

```
👤 你：这周有什么安排
🤖 助手：本周共有 3 个日程：
  1. 团队周会 - 2026-03-10 15:00~16:00
  2. 项目评审 - 2026-03-12 10:00~11:00
  3. 客户会议 - 2026-03-14 14:00~15:00
```

### 修改日程

```
👤 你：把周会的会议改到 4 点
🤖 助手：已更新日程：团队周会
```

### 删除日程

```
👤 你：取消明天的会议
🤖 助手：已删除日程：团队会议
```

### 解析文档

```
👤 你：帮我解析这个日程安排：
- 3月15日上午10点项目评审
- 3月20日下午2点客户会议
🤖 助手：已从文档中提取 2 条日程信息...
```

## 🛠️ 工具说明

| 工具 | 功能 | 参数 |
|------|------|------|
| add_event | 添加日程 | title, start_time, end_time, description, location, reminder |
| modify_event | 修改日程 | event_id, title, start_time, end_time, description, location |
| query_event | 查询日程 | start_date, end_date, keyword |
| delete_event | 删除日程 | event_id |
| parse_document | 解析文档 | content, source_type |

## 📁 数据存储

日程数据保存在 `data/events.json` 文件中，格式如下：

```json
{
  "abc12345": {
    "event_id": "abc12345",
    "title": "团队会议",
    "start_time": "2026-03-10 15:00",
    "end_time": "2026-03-10 16:00",
    "description": "讨论 Q2 计划",
    "location": "会议室 A",
    "reminder": 15,
    "created_at": "2026-03-09T10:30:00"
  }
}
```

## 🧪 测试

运行测试套件：

```bash
source .venv/bin/activate
pytest tests/ -v
```

## 📝 时间格式支持

支持多种时间表达方式：

- 标准格式：`2026-03-10 15:00`
- 相对时间：`明天 15:00`、`下周一`
- 日期范围：`2026-03-10 15:00~16:00`

## ✨ 功能特性

### 冲突检测

创建或修改日程时，系统会自动检测时间冲突：

```python
from src.event_manager import EventManager

manager = EventManager()
conflicts = manager.check_conflict("2026-03-15 10:00", "2026-03-15 11:00")
```

### 文档解析

从 Markdown 文件或文本中提取日程：

```python
from src.event_manager import parse_document_binding

# 解析文本
result = parse_document_binding("明天下午3点开会讨论项目", "text")

# 解析文件
result = parse_document_binding("notes.md", "file")
```

## 🔧 扩展功能

### 添加新工具

1. 在 `tools/` 目录创建 YAML 文件
2. 在 `src/` 目录实现绑定函数
3. 在 `config.yaml` 中注册工具

### 添加新 Skill

1. 创建 `skills/your-skill/SKILL.md` 文件
2. 按照上述格式编写 YAML frontmatter 和内容
3. 在 `config.yaml` 的 `skills` 列表中添加路径

### 集成文档解析

```python
from src.doc_parser import ScheduleParser

parser = ScheduleParser()
schedules = parser.parse_markdown_file("notes.md")
```

### 启用可观测性

在 `.env` 中配置 Langfuse：

```bash
LANGFUSE_SECRET_KEY="sk-lf-xxx"
LANGFUSE_PUBLIC_KEY="pk-lf-xxx"
LANGFUSE_HOST="https://cloud.langfuse.com"
```

## ❓ 常见问题

**Q: 如何切换 LLM 模型？**
A: 修改 `.env` 文件中的 `LLM_MODEL`、`LLM_BASE_URL` 和 `LLM_API_KEY`。

**Q: 日程数据会同步到云端吗？**
A: 默认保存在本地 `data/events.json`，可自行实现云端同步。

**Q: 如何设置提醒？**
A: 创建日程时通过 `reminder` 参数设置提前提醒时间（分钟）。

**Q: 如何检测日程冲突？**
A: 使用 `check_conflict()` 方法或通过智能体询问。

**Q: Skill 是必需的吗？**
A: 不是。Skill 是可选的增强功能，用于提升 AI 的专业理解能力。即使没有 Skill，工具也能正常工作。

**Q: Skill 和 System Prompt 有什么区别？**
A: System Prompt 定义 AI 的人设和工作流程，而 Skill 提供特定领域的专业知识和工具使用指导。

**Q: 如何调试 Skill 是否生效？**
A: 在启动时查看日志，确认 Skill 被成功加载。也可以通过观察 AI 是否能更准确地调用工具来判断。

**Q: 一个项目可以有多个 Skill 吗？**
A: 可以。在 `config.yaml` 的 `skills` 列表中添加多个路径即可。

## 📄 许可证

MIT License