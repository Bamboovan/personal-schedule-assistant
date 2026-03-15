import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nexau import Agent, AgentConfig, LLMConfig, Tool
from nexau.archs.main_sub.execution.hooks import LoggingMiddleware
from nexau.archs.main_sub.context_value import ContextValue
from nexau.archs.tracer.adapters import LangfuseTracer

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
    parse_document_binding,
)

# 配置工具
tools = [
    Tool.from_yaml(base_dir / "tools/add_event.tool.yaml", binding=add_event_binding),
    Tool.from_yaml(base_dir / "tools/modify_event.tool.yaml", binding=modify_event_binding),
    Tool.from_yaml(base_dir / "tools/query_event.tool.yaml", binding=query_event_binding),
    Tool.from_yaml(base_dir / "tools/delete_event.tool.yaml", binding=delete_event_binding),
    Tool.from_yaml(base_dir / "tools/parse_document.tool.yaml", binding=parse_document_binding),
]

# 配置 LLM
llm_config = LLMConfig(
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
    model=os.getenv("LLM_MODEL"),
    base_url=os.getenv("LLM_BASE_URL"),
    api_key=os.getenv("LLM_API_KEY"),
    api_type="openai_chat_completion",
)

# 读取系统提示词
system_prompt_path = base_dir / "system-prompt.md"

# 配置 Langfuse Tracer
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

tracers = []
if langfuse_public_key and langfuse_secret_key:
    tracer = LangfuseTracer(
        public_key=langfuse_public_key,
        secret_key=langfuse_secret_key,
        host=langfuse_host,
    )
    tracers.append(tracer)

# 配置代理
agent_config = AgentConfig(
    name="personal-schedule-assistant",
    max_context_tokens=100000,
    system_prompt=str(system_prompt_path),
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
    tracers=tracers if tracers else None,
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
        try:
            user_input = input("👤 你：")
            if user_input.lower() in ['quit', 'exit', '退出']:
                break

            # 注入当前日期到提示词
            current_date = datetime.now().strftime("%Y 年%m 月%d 日 %A")
            variables = ContextValue(template={"current_date": current_date})
            
            response = agent.run(message=user_input, variables=variables)
            print(f"🤖 助手：{response}\n")
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"❌ 错误：{e}\n")
