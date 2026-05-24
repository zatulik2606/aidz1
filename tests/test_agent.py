import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from bot.agent import run_agent
from src.config import Config


class AgentLoopTests(unittest.TestCase):
    @patch("bot.agent.AsyncOpenAI")
    def test_agent_returns_direct_answer_without_tool_calls(
        self,
        mock_client_cls,
    ) -> None:
        mock_client = mock_client_cls.return_value
        completion = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="Готово.",
                        tool_calls=[],
                    )
                )
            ]
        )
        mock_client.chat.completions.create = AsyncMock(return_value=completion)
        config = Config(
            telegram_bot_token="token",
            llm_provider="openrouter",
            llm_base_url="https://openrouter.ai/api/v1",
            llm_api_key="key",
            llm_text_model="openai/gpt-4o-mini",
            llm_image_model="openai/gpt-4o-mini",
            llm_transcribe_model="openai/gpt-4o-transcribe",
            embedding_model="openai/text-embedding-3-small",
            system_prompt_text="text prompt",
            system_prompt_image="image prompt",
            system_prompt_audio="audio prompt",
            leads_db_path="./data/leads.db",
            chroma_path="./data/chroma",
            langsmith_enabled=False,
            langsmith_api_key="",
            langsmith_project="",
            tavily_api_key="",
        )

        result = asyncio.run(
            run_agent(
                history=[{"role": "user", "content": "Привет"}],
                config=config,
            )
        )
        self.assertEqual(result, "Готово.")

    @patch("bot.agent.AsyncOpenAI")
    def test_agent_runs_tool_call_and_builds_final_answer(
        self,
        mock_client_cls,
    ) -> None:
        mock_client = mock_client_cls.return_value
        tool_call = SimpleNamespace(
            id="tool_1",
            function=SimpleNamespace(name="web_search", arguments='{"query":"Python 3.12"}'),
        )
        first_completion = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="",
                        tool_calls=[tool_call],
                    )
                )
            ]
        )
        second_completion = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="Проверил факт и сформировал ответ.",
                        tool_calls=[],
                    )
                )
            ]
        )
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[first_completion, second_completion]
        )
        config = Config(
            telegram_bot_token="token",
            llm_provider="openrouter",
            llm_base_url="https://openrouter.ai/api/v1",
            llm_api_key="key",
            llm_text_model="openai/gpt-4o-mini",
            llm_image_model="openai/gpt-4o-mini",
            llm_transcribe_model="openai/gpt-4o-transcribe",
            embedding_model="openai/text-embedding-3-small",
            system_prompt_text="text prompt",
            system_prompt_image="image prompt",
            system_prompt_audio="audio prompt",
            leads_db_path="./data/leads.db",
            chroma_path="./data/chroma",
            langsmith_enabled=False,
            langsmith_api_key="",
            langsmith_project="",
            tavily_api_key="",
        )

        result = asyncio.run(
            run_agent(
                history=[{"role": "user", "content": "Проверь актуальность Python 3.12"}],
                config=config,
            )
        )
        self.assertEqual(result, "Проверил факт и сформировал ответ.")
        self.assertEqual(mock_client.chat.completions.create.await_count, 2)

