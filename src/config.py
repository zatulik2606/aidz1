from dataclasses import dataclass
import os

from dotenv import load_dotenv


REQUIRED_VARS = (
    "TELEGRAM_BOT_TOKEN",
    "LLM_PROVIDER",
    "LLM_BASE_URL",
    "LLM_API_KEY",
    "LLM_MODEL",
    "SYSTEM_PROMPT",
)


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    llm_provider: str
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    system_prompt: str


def load_config() -> Config:
    load_dotenv()

    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(f"Missing required env vars: {missing_text}")

    return Config(
        telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        llm_provider=os.environ["LLM_PROVIDER"],
        llm_base_url=os.environ["LLM_BASE_URL"],
        llm_api_key=os.environ["LLM_API_KEY"],
        llm_model=os.environ["LLM_MODEL"],
        system_prompt=os.environ["SYSTEM_PROMPT"],
    )
