from pathlib import Path

import chromadb
from openai import AsyncOpenAI

from src.config import Config
from src.rag.indexer import COLLECTION_NAME


async def search_company_docs(query: str, config: Config, top_k: int = 3) -> list[dict[str, str]]:
    text = query.strip()
    if not text:
        return []

    chroma_path = Path(config.chroma_path)
    if not chroma_path.exists():
        return []

    openai_client = AsyncOpenAI(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
    )
    embedding_response = await openai_client.embeddings.create(
        model=config.embedding_model,
        input=[text],
    )
    query_embedding = embedding_response.data[0].embedding

    client = chromadb.PersistentClient(path=str(chroma_path))
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    rows: list[dict[str, str]] = []
    for doc, metadata in zip(documents, metadatas):
        source = str((metadata or {}).get("source", "unknown"))
        rows.append(
            {
                "source": source,
                "snippet": (doc or "").strip(),
            }
        )
    return rows
