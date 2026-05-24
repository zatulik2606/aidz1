import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import AsyncOpenAI

from src.config import Config
from src.tools.capture_lead import capture_lead
from src.tools.rag import rag_search
from src.tools.web_search import web_search


logger = logging.getLogger(__name__)

ToolCallable = Callable[..., Awaitable[str]]
MAX_AGENT_STEPS = 5

TOOLS_SPEC: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "rag_search",
            "description": "Поиск по внутренним документам компании.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Проверка актуальных фактов из интернета.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Фиксация заявки пользователя на консультацию.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "contact": {"type": "string"},
                    "request_text": {"type": "string"},
                    "source_chat_id": {"type": "integer"},
                },
                "required": ["name", "contact", "request_text"],
                "additionalProperties": False,
            },
        },
    },
]

TOOL_HANDLERS: dict[str, ToolCallable] = {
    "rag_search": rag_search,
    "web_search": web_search,
    "capture_lead": capture_lead,
}


def _normalize_model_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"].strip())
        return "\n".join(item for item in chunks if item).strip()
    return ""


def _build_messages(history: list[dict[str, Any]], config: Config) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": config.system_prompt_text},
        {
            "role": "system",
            "content": (
                "Отвечай строго на русском языке. "
                "Не переключайся на английский даже при англоязычном вводе."
            ),
        },
        *history,
    ]


async def _execute_tool(tool_call: Any) -> dict[str, Any]:
    tool_name = tool_call.function.name
    raw_arguments = tool_call.function.arguments or "{}"
    tool_call_id = tool_call.id

    if tool_name not in TOOL_HANDLERS:
        logger.warning("Unknown tool requested: %s", tool_name)
        result_text = "Инструмент недоступен."
    else:
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError:
            logger.warning("Tool arguments are not valid JSON for %s", tool_name)
            arguments = {}
        if tool_name == "capture_lead":
            arguments.setdefault("leads_db_path", tool_call.leads_db_path)
            arguments.setdefault("source_chat_id", tool_call.source_chat_id)
        try:
            result_text = await TOOL_HANDLERS[tool_name](**arguments)
        except Exception:
            logger.exception("Tool execution failed: %s", tool_name)
            result_text = "Инструмент временно недоступен."

    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": tool_name,
        "content": result_text,
    }


@traceable(name="agent_loop")
async def _run_agent_traceable(history: list[dict[str, Any]], config: Config) -> str:
    return await _run_agent_impl(history=history, config=config)


async def _run_agent_impl(history: list[dict[str, Any]], config: Config) -> str:
    base_client = AsyncOpenAI(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
    )
    client = wrap_openai(base_client) if config.langsmith_enabled else base_client
    messages = _build_messages(history=history, config=config)
    step = 0

    while step < MAX_AGENT_STEPS:
        response = await client.chat.completions.create(
            model=config.llm_text_model,
            messages=messages,
            tools=TOOLS_SPEC,
        )
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls or []
        content_text = _normalize_model_content(assistant_message.content)

        if not tool_calls:
            return content_text

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in tool_calls
                ],
            }
        )

        for tool_call in tool_calls:
            tool_call.leads_db_path = config.leads_db_path
            tool_call.source_chat_id = next(
                (
                    msg.get("chat_id")
                    for msg in reversed(messages)
                    if isinstance(msg, dict)
                    and msg.get("role") == "user"
                    and isinstance(msg.get("chat_id"), int)
                ),
                None,
            )
            tool_message = await _execute_tool(tool_call)
            messages.append(tool_message)

        step += 1

    return "Не удалось завершить обработку запроса, попробуйте еще раз."


async def run_agent(history: list[dict[str, Any]], config: Config) -> str:
    if config.langsmith_enabled:
        return await _run_agent_traceable(history=history, config=config)
    return await _run_agent_impl(history=history, config=config)
