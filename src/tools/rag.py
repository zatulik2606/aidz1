from src.config import load_config
from src.rag.retriever import search_company_docs


async def rag_search(query: str) -> str:
    text = query.strip()
    if not text:
        return "RAG-поиск: запрос пустой."

    config = load_config()
    rows = await search_company_docs(query=text, config=config, top_k=3)
    if not rows:
        return "По базе документов ничего не найдено. Сначала выполните индексацию PDF."

    lines = ["Найдено в документах компании:"]
    for idx, row in enumerate(rows, 1):
        snippet = row["snippet"].replace("\n", " ").strip()
        short = snippet[:260] + ("..." if len(snippet) > 260 else "")
        lines.append(f"{idx}. [{row['source']}] {short}")
    return "\n".join(lines)
