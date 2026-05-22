from bot.agent import run_agent
from src.config import Config


async def generate_reply(
    user_text: str,
    history: list[dict[str, str]],
    config: Config,
) -> str:
    return await run_agent(
        history=[*history, {"role": "user", "content": user_text}],
        config=config,
    )
