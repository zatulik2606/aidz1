import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.audio_client import generate_audio_reply
from src.config import Config


class AudioClientTests(unittest.TestCase):
    @patch("src.audio_client.AsyncOpenAI")
    def test_generate_audio_reply_calls_transcribe_api(self, mock_client_cls) -> None:
        mock_client = mock_client_cls.return_value
        mock_transcribe = AsyncMock(
            return_value=SimpleNamespace(text="transcribed text")
        )
        mock_client.audio.transcriptions.create = mock_transcribe

        config = Config(
            telegram_bot_token="token",
            llm_provider="openrouter",
            llm_base_url="https://openrouter.ai/api/v1",
            llm_api_key="key",
            llm_text_model="openai/gpt-4o-mini",
            llm_image_model="openai/gpt-4o-mini",
            llm_transcribe_model="openai/gpt-4o-transcribe",
            system_prompt_text="text prompt",
            system_prompt_image="image prompt",
            system_prompt_audio="audio prompt",
        )
        result = asyncio.run(
            generate_audio_reply(
                audio_bytes=b"audio-bytes",
                config=config,
                audio_format="ogg",
            )
        )

        self.assertEqual(result, "transcribed text")
        _, kwargs = mock_transcribe.call_args
        self.assertEqual(kwargs["model"], "openai/gpt-4o-transcribe")
        self.assertEqual(kwargs["prompt"], "audio prompt")
        self.assertEqual(kwargs["language"], "ru")
        self.assertTrue(kwargs["file"])
