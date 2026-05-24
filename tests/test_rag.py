import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.config import Config
from src.rag.retriever import search_company_docs


class RagTests(unittest.TestCase):
    @patch("src.rag.retriever.chromadb.PersistentClient")
    @patch("src.rag.retriever.AsyncOpenAI")
    def test_search_company_docs_returns_rows(self, mock_openai_cls, mock_chroma_cls) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            chroma_path = Path(tmp_dir) / "chroma"
            chroma_path.mkdir(parents=True, exist_ok=True)

            mock_client = mock_openai_cls.return_value
            mock_client.embeddings.create = AsyncMock(
                return_value=SimpleNamespace(
                    data=[SimpleNamespace(embedding=[0.1, 0.2, 0.3])]
                )
            )

            mock_collection = mock_chroma_cls.return_value.get_collection.return_value
            mock_collection.query.return_value = {
                "documents": [["Фрагмент из PDF"]],
                "metadatas": [[{"source": "company.pdf"}]],
            }

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
                chroma_path=str(chroma_path),
                langsmith_enabled=False,
                langsmith_api_key="",
                langsmith_project="",
            )

            rows = asyncio.run(
                search_company_docs(
                    query="Что по услугам?",
                    config=config,
                    top_k=1,
                )
            )

            self.assertEqual(
                rows,
                [{"source": "company.pdf", "snippet": "Фрагмент из PDF"}],
            )
