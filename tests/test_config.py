import os
import unittest
from unittest.mock import patch

from src.config import load_config


class ConfigTests(unittest.TestCase):
    @patch("src.config.load_dotenv")
    @patch("src.config.dotenv_values", return_value={})
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "LLM_PROVIDER": "openrouter",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_API_KEY": "key",
            "SYSTEM_PROMPT_TEXT": "text prompt",
        },
        clear=True,
    )
    def test_load_config_fails_without_text_model(
        self,
        _mock_dotenv_values,
        _mock_load_dotenv,
    ) -> None:
        with self.assertRaises(RuntimeError) as context:
            load_config()
        self.assertIn("LLM_TEXT_MODEL", str(context.exception))

    @patch("src.config.load_dotenv")
    @patch("src.config.dotenv_values", return_value={})
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "LLM_PROVIDER": "openrouter",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_API_KEY": "key",
            "LLM_TEXT_MODEL": "openai/gpt-4o-mini",
            "LLM_IMAGE_MODEL": "openai/gpt-4o-mini",
            "LLM_TRANSCRIBE_MODEL": "openai/gpt-4o-transcribe",
            "SYSTEM_PROMPT_AUDIO": "audio prompt",
            "SYSTEM_PROMPT_TEXT": "text prompt",
            "SYSTEM_PROMPT_IMAGE": "image prompt",
        },
        clear=True,
    )
    def test_load_config_langsmith_defaults(
        self,
        _mock_dotenv_values,
        _mock_load_dotenv,
    ) -> None:
        config = load_config()
        self.assertFalse(config.langsmith_enabled)
        self.assertEqual(config.langsmith_api_key, "")
        self.assertEqual(config.langsmith_project, "")
        self.assertEqual(config.leads_db_path, "./data/leads.db")
        self.assertEqual(config.chroma_path, "./data/chroma")
        self.assertEqual(config.tavily_api_key, "")

    @patch("src.config.load_dotenv")
    @patch("src.config.dotenv_values", return_value={})
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "LLM_PROVIDER": "openrouter",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_API_KEY": "key",
            "LLM_MODEL": "openai/gpt-4o-mini",
            "SYSTEM_PROMPT_TEXT": "text prompt",
        },
        clear=True,
    )
    def test_load_config_supports_llm_model_fallback(
        self,
        _mock_dotenv_values,
        _mock_load_dotenv,
    ) -> None:
        config = load_config()
        self.assertEqual(config.llm_text_model, "openai/gpt-4o-mini")
        self.assertEqual(config.llm_image_model, "openai/gpt-4o-mini")

    @patch("src.config.load_dotenv")
    @patch("src.config.dotenv_values", return_value={})
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "LLM_PROVIDER": "openrouter",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_API_KEY": "key",
            "LLM_MODEL": "openai/gpt-4o-mini",
            "SYSTEM_PROMPT_TEXT": "text prompt",
            "LANGCHAIN_TRACING_V2": "true",
            "LANGCHAIN_API_KEY": "ls-key",
            "LANGCHAIN_PROJECT": "agent-project",
        },
        clear=True,
    )
    def test_load_config_supports_langchain_env_aliases(
        self,
        _mock_dotenv_values,
        _mock_load_dotenv,
    ) -> None:
        config = load_config()
        self.assertTrue(config.langsmith_enabled)
        self.assertEqual(config.langsmith_api_key, "ls-key")
        self.assertEqual(config.langsmith_project, "agent-project")

    @patch("src.config.load_dotenv")
    @patch("src.config.dotenv_values", return_value={})
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "LLM_PROVIDER": "openrouter",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_API_KEY": "key",
            "LLM_MODEL": "openai/gpt-4o-mini",
            "SYSTEM_PROMPT_TEXT": "text prompt",
            "TAVILY_API_KEY": "tavily-key",
        },
        clear=True,
    )
    def test_load_config_reads_tavily_api_key(
        self,
        _mock_dotenv_values,
        _mock_load_dotenv,
    ) -> None:
        config = load_config()
        self.assertEqual(config.tavily_api_key, "tavily-key")

    @patch("src.config.load_dotenv")
    @patch("src.config.dotenv_values", return_value={"TAVILY_API_KEY": "dotenv-key"})
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "LLM_PROVIDER": "openrouter",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_API_KEY": "key",
            "LLM_MODEL": "openai/gpt-4o-mini",
            "SYSTEM_PROMPT_TEXT": "text prompt",
            "TAVILY_API_KEY": "",
        },
        clear=True,
    )
    def test_load_config_reads_tavily_key_from_dotenv_when_env_empty(
        self,
        _mock_dotenv_values,
        _mock_load_dotenv,
    ) -> None:
        config = load_config()
        self.assertEqual(config.tavily_api_key, "dotenv-key")
