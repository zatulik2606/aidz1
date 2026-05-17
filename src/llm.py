from openai import AsyncOpenAI

from src.config import Config


async def generate_reply(
    user_text: str,
    history: list[dict[str, str]],
    config: Config,
) -> str:
    client = AsyncOpenAI(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": config.system_prompt_text},
        *history,
        {"role": "user", "content": user_text},
    ]
    response = await client.chat.completions.create(
        model=config.llm_text_model,
        messages=messages,
    )
    content = response.choices[0].message.content
    return (content or "").strip()
