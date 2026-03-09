# 个人日程助手智能体

基于 **NexAU** 框架的个人日程管理智能体，能够从聊天记录和文档中自动创建、修改、查询和删除日程。

## 📁 项目结构

```
personal-assistant/
├── .env.example            # 环境变量模板
├── config.yaml             # 智能体配置文件
├── main.py                 # 启动脚本
├── system-prompt.md        # 系统提示词
├── tools/                  # 工具定义
│   ├── add_event.tool.yaml
│   ├── modify_event.tool.yaml
│   ├── query_event.tool.yaml
│   └── delete_event.tool.yaml
├── src/                    # 核心实现
│   ├── event_manager.py    # 日程管理
│   └── doc_parser.py       # 文档解析
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
vim .env
# 编辑 .env 文件，填入你的 API 密钥
```

推荐使用 Qwen 系列模型：
```bash
LLM_MODEL="qwen-plus"
LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_API_KEY="your-dashscope-api-key"
```

### 2. 安装依赖

```bash
pip install python-dotenv
# NexAU 框架已包含在 NexAU-main 目录中
```

### 3. 运行智能体

```bash
python main.py
```

### 4. 测试

```bash
pytest tests/test_schedule_assistant.py -v
```

## 💡 功能特性

- ✅ **添加日程** - 支持自然语言时间表达
- ✅ **修改日程** - 更新日程时间、标题、描述等
- ✅ **查询日程** - 按日期范围和关键词搜索
- ✅ **删除日程** - 安全删除日程
- ✅ **文档解析** - 从 Markdown/聊天记录提取日程

## 📝 使用示例

```
👤 你：明天下午 3 点到 4 点有个团队会议，帮我创建日程
🤖 助手：已创建日程：团队会议 (event_id: abc12345)

👤 你：这周有什么安排
🤖 助手：本周共有 3 个日程...

👤 你：把周会的会议改到 4 点
🤖 助手：已更新日程：团队周会
```

## 📖 详细文档

查看 [docs/user-guide.md](docs/user-guide.md) 获取完整使用指南。

## 🧪 测试状态

- ✅ 添加日程测试通过
- ✅ 查询日程测试通过
- ✅ 修改日程测试通过
- ✅ 删除日程测试通过
- ✅ 文档解析器测试通过

## 🔧 工具说明

| 工具 | 功能 | 必需参数 |
|------|------|----------|
| `add_event` | 添加日程 | title, start_time, end_time |
| `modify_event` | 修改日程 | event_id |
| `query_event` | 查询日程 | start_date, end_date |
| `delete_event` | 删除日程 | event_id |

## 📄 许可证

MIT License
