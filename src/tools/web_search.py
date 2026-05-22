async def web_search(query: str) -> str:
    text = query.strip()
    if not text:
        return "Веб-поиск: запрос пустой."
    return (
        "Веб-поиск пока работает в базовом режиме. "
        f"Запрос принят: {text}"
    )
