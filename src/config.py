from dataclasses import dataclass
import os

from dotenv import load_dotenv


REQUIRED_BASE_VARS = (
    "TELEGRAM_BOT_TOKEN",
    "LLM_PROVIDER",
    "LLM_BASE_URL",
    "LLM_API_KEY",
)


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    llm_provider: str
    llm_base_url: str
    llm_api_key: str
    llm_text_model: str
    llm_image_model: str
    llm_transcribe_model: str
    embedding_model: str
    system_prompt_text: str
    system_prompt_image: str
    system_prompt_audio: str
    leads_db_path: str
    chroma_path: str
    langsmith_enabled: bool
    langsmith_api_key: str
    langsmith_project: str


def _first_non_empty(*values: str) -> str:
    for value in values:
        if value:
            return value
    return ""


def _load_prompt_from_path(path: str) -> str:
    if not path:
        return ""
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().strip()
    except OSError:
        return ""


def load_config() -> Config:
    load_dotenv()

    missing = [name for name in REQUIRED_BASE_VARS if not os.getenv(name)]
    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(f"Missing required env vars: {missing_text}")

    llm_text_model = _first_non_empty(
        os.getenv("LLM_TEXT_MODEL", ""),
        os.getenv("LLM_MODEL", ""),
        os.getenv("MODEL_TEXT", ""),
    )
    llm_image_model = _first_non_empty(
        os.getenv("LLM_IMAGE_MODEL", ""),
        os.getenv("LLM_MODEL", ""),
        os.getenv("MODEL_IMAGE", ""),
        llm_text_model,
    )
    llm_transcribe_model = _first_non_empty(
        os.getenv("LLM_TRANSCRIBE_MODEL", ""),
        "openai/gpt-4o-transcribe",
    )

    prompt_from_path = _load_prompt_from_path(os.getenv("SYSTEM_PROMPT_PATH", ""))
    system_prompt_text = _first_non_empty(
        os.getenv("SYSTEM_PROMPT_TEXT", ""),
        prompt_from_path,
    )
    system_prompt_image = _first_non_empty(
        os.getenv("SYSTEM_PROMPT_IMAGE", ""),
        system_prompt_text,
    )
    system_prompt_audio = _first_non_empty(
        os.getenv("SYSTEM_PROMPT_AUDIO", ""),
        system_prompt_text,
    )

    if not llm_text_model:
        raise RuntimeError(
            "Missing required env vars: LLM_TEXT_MODEL (or LLM_MODEL / MODEL_TEXT)"
        )
    if not system_prompt_text:
        raise RuntimeError(
            "Missing required env vars: SYSTEM_PROMPT_TEXT (or SYSTEM_PROMPT_PATH)"
        )

    langsmith_enabled = _first_non_empty(
        os.getenv("LANGSMITH_ENABLED", ""),
        os.getenv("LANGCHAIN_TRACING_V2", "false"),
    ).lower() == "true"
    langsmith_api_key = _first_non_empty(
        os.getenv("LANGSMITH_API_KEY", ""),
        os.getenv("LANGCHAIN_API_KEY", ""),
    )
    langsmith_project = _first_non_empty(
        os.getenv("LANGSMITH_PROJECT", ""),
        os.getenv("LANGCHAIN_PROJECT", ""),
    )

    return Config(
        telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        llm_provider=os.environ["LLM_PROVIDER"],
        llm_base_url=os.environ["LLM_BASE_URL"],
        llm_api_key=os.environ["LLM_API_KEY"],
        llm_text_model=llm_text_model,
        llm_image_model=llm_image_model,
        llm_transcribe_model=llm_transcribe_model,
        embedding_model=os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small"),
        system_prompt_text=system_prompt_text,
        system_prompt_image=system_prompt_image,
        system_prompt_audio=system_prompt_audio,
        leads_db_path=os.getenv("LEADS_DB_PATH", "./data/leads.db"),
        chroma_path=os.getenv("CHROMA_PATH", "./data/chroma"),
        langsmith_enabled=langsmith_enabled,
        langsmith_api_key=langsmith_api_key,
        langsmith_project=langsmith_project,
    )
