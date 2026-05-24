from pathlib import Path
import hashlib

import chromadb
import pymupdf4llm
from openai import AsyncOpenAI

from src.config import Config


COLLECTION_NAME = "company_docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _chunk_text(text: str) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + CHUNK_SIZE, len(normalized))
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(0, end - CHUNK_OVERLAP)
    return chunks


def _pdf_paths(data_dir: Path) -> list[Path]:
    return sorted(path for path in data_dir.glob("*.pdf") if path.is_file())


def _stable_id(file_name: str, idx: int, chunk: str) -> str:
    digest = hashlib.sha1(chunk.encode("utf-8")).hexdigest()[:12]
    return f"{file_name}:{idx}:{digest}"


async def ingest_company_pdfs(config: Config) -> int:
    data_dir = Path("data")
    pdf_paths = _pdf_paths(data_dir)
    if not pdf_paths:
        return 0

    chroma_path = Path(config.chroma_path)
    chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_path))
    # Recreate collection on each ingest to keep index deterministic.
    client.delete_collection(name=COLLECTION_NAME)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    openai_client = AsyncOpenAI(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
    )

    indexed = 0
    for pdf_path in pdf_paths:
        markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
        chunks = _chunk_text(markdown_text)
        if not chunks:
            continue
        embeddings_response = await openai_client.embeddings.create(
            model=config.embedding_model,
            input=chunks,
        )
        embeddings = [row.embedding for row in embeddings_response.data]
        ids = [_stable_id(pdf_path.name, i, chunk) for i, chunk in enumerate(chunks)]
        metadatas = [{"source": pdf_path.name, "chunk_index": i} for i in range(len(chunks))]
        collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        indexed += len(chunks)

    return indexed
