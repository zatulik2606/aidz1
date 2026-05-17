import os
import unittest
from unittest.mock import patch

from src.config import load_config


class ConfigTests(unittest.TestCase):
    @patch("src.config.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "token",
            "LLM_PROVIDER": "openrouter",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_API_KEY": "key",
            "LLM_TEXT_MODEL": "openai/gpt-4o-mini",
            "LLM_IMAGE_MODEL": "openai/gpt-4o-mini",
            "SYSTEM_PROMPT_AUDIO": "audio prompt",
            "SYSTEM_PROMPT_TEXT": "text prompt",
            "SYSTEM_PROMPT_IMAGE": "image prompt",
        },
        clear=True,
    )
    def test_load_config_fails_without_transcribe_model(self, _mock_load_dotenv) -> None:
        with self.assertRaises(RuntimeError) as context:
            load_config()
        self.assertIn("LLM_TRANSCRIBE_MODEL", str(context.exception))
