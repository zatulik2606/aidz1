async def rag_search(query: str) -> str:
    text = query.strip()
    if not text:
        return "RAG-поиск: запрос пустой."
    return (
        "RAG-поиск пока работает в базовом режиме. "
        f"Запрос принят: {text}"
    )
