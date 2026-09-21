import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

SYSTEM_PROMPT = (
    "You are an AI operations assistant for a backend engineering team. "
    "You have tools to inspect job runs (failures, logs, search, stats) via MCP. "
    "Always call a tool to get real data before answering questions about jobs, "
    "failures, or service health -- never guess. Summarize findings concisely "
    "and mention job ids and services when relevant."
)

_client: MultiServerMCPClient | None = None
_agent = None


def _mcp_server_config() -> dict:
    url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    return {
        "jobs": {
            "url": url,
            "transport": "streamable_http",
        }
    }


async def get_agent():
    """Lazily build (once) and return the LangGraph agent, backed by live MCP tools."""
    global _client, _agent
    if _agent is not None:
        return _agent

    _client = MultiServerMCPClient(_mcp_server_config())
    tools = await _client.get_tools()

    model = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0,
    )

    _agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)
    return _agent


async def ask(message: str) -> str:
    agent = await get_agent()
    result = await agent.ainvoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content
