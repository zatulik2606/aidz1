from src.config import load_config
from src.rag.retriever import search_company_docs
from src.telegram_text import sanitize_telegram_text


def _langsmith_extra(thread_id: str | None) -> dict:
    if not thread_id:
        return {}
    return {
        "metadata": {"thread_id": thread_id},
        "tags": [f"thread_id:{thread_id}"],
    }


async def rag_search(query: str, thread_id: str | None = None) -> str:
    text = query.strip()
    if not text:
        return "RAG-поиск: запрос пустой."

    config = load_config()
    rows = await search_company_docs(
        query=text,
        config=config,
        top_k=3,
        thread_id=thread_id,
        langsmith_extra=_langsmith_extra(thread_id),
    )
    if not rows:
        return "По базе документов ничего не найдено. Сначала выполните индексацию PDF."

    lines = ["Найдено в документах компании:"]
    for idx, row in enumerate(rows, 1):
        snippet = sanitize_telegram_text(row["snippet"]).replace("\n", " ").strip()
        short = snippet[:260] + ("..." if len(snippet) > 260 else "")
        lines.append(f"{idx}. [{row['source']}] {short}")
    return "\n".join(lines)
