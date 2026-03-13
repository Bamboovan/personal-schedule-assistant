# 个人日程助手智能体

基于 **NexAU** 框架的个人日程管理智能体，能够从聊天记录和文档中自动创建、修改、查询和删除日程。

## 📁 项目结构

```
personal-assistant/
├── .env.example            # 环境变量模板
├── config.yaml             # 智能体配置文件
├── main.py                 # 启动脚本
├── system-prompt.md        # 系统提示词
├── requirements.txt        # 依赖列表
├── tools/                  # 工具定义
│   ├── add_event.tool.yaml
│   ├── modify_event.tool.yaml
│   ├── query_event.tool.yaml
│   ├── delete_event.tool.yaml
│   └── parse_document.tool.yaml
├── src/                    # 核心实现
│   ├── event_manager.py    # 日程管理
│   └── doc_parser.py       # 文档解析
├── skills/                 # 技能定义
│   └── schedule-skill/
│       ├── skill.md
│       ├── examples.md
│       └── prompts/extract_schedule.md
├── data/                   # 数据存储
│   └── events.json         # 日程数据
├── tests/                  # 测试文件
│   └── test_schedule_assistant.py
└── docs/                   # 文档
    └── user-guide.md
```

## 🚀 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
```

推荐使用 Qwen 系列模型：
```bash
LLM_MODEL="qwen-plus"
LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_API_KEY="your-dashscope-api-key"
```

### 2. 安装依赖

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

### 3. 运行智能体

```bash
source .venv/bin/activate
python main.py
```

### 4. 运行测试

```bash
source .venv/bin/activate
pytest tests/ -v
```

## 💡 功能特性

- ✅ **添加日程** - 支持自然语言时间表达
- ✅ **修改日程** - 更新日程时间、标题、描述等
- ✅ **查询日程** - 按日期范围和关键词搜索
- ✅ **删除日程** - 安全删除日程
- ✅ **文档解析** - 从 Markdown/聊天记录提取日程
- ✅ **冲突检测** - 创建/修改时检测时间冲突
- ✅ **数据安全** - 文件锁防止并发写入损坏

## 📝 使用示例

```
👤 你：明天下午 3 点到 4 点有个团队会议，帮我创建日程
🤖 助手：已创建日程：团队会议 (event_id: abc12345)

👤 你：这周有什么安排
🤖 助手：本周共有 3 个日程...

👤 你：把周会的会议改到 4 点
🤖 助手：已更新日程：团队周会
```

## 🔧 工具说明

| 工具 | 功能 | 必需参数 |
|------|------|----------|
| `add_event` | 添加日程 | title, start_time, end_time |
| `modify_event` | 修改日程 | event_id |
| `query_event` | 查询日程 | start_date, end_date |
| `delete_event` | 删除日程 | event_id |
| `parse_document` | 解析文档提取日程 | content, source_type |

## 📖 详细文档

查看 [docs/user-guide.md](docs/user-guide.md) 获取完整使用指南。

## 🧪 测试状态

- ✅ 添加日程测试通过
- ✅ 查询日程测试通过
- ✅ 修改日程测试通过
- ✅ 删除日程测试通过
- ✅ 文档解析器测试通过

---

## 📋 更新日志

### v1.1.0 (2026-03-13)

#### P0 关键修复
- 修复 `doc_parser.py` 正则表达式 `|` 符号空格问题
- 统一 `config.yaml` 与 `main.py` 配置（`system_prompt_type: jinja`）
- 修复测试隔离问题，使用独立实例而非全局变量

#### P1 代码质量
- 添加完整类型注解（`TypedDict`、函数签名）
- 新增异常类：`EventError`、`InvalidTimeFormatError`、`InvalidTimeRangeError`
- 添加时间格式验证和范围校验
- 所有模块添加 RFC 风格文档字符串

#### P2 功能完善
- 新增 `parse_document` 工具，支持文档解析
- 新增 `EventManager.check_conflict()` 日程冲突检测
- 使用 `fcntl` 实现文件锁，防止并发写入损坏
- 完善 Skill 文件（`skill.md`、`examples.md`、提示词模板）

#### P3 架构优化
- 新增 `requirements.txt`，从 GitHub 安装 NexAU
- 启用 Langfuse 可观测性追踪
- 新增 GitHub Actions CI/CD 配置
- 移除本地 `NexAU-main/` 目录，改用包管理

---

## 📄 许可证

MIT License