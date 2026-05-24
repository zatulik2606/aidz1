import asyncio
import json
import urllib.error
import urllib.request

from src.config import load_config

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def _perform_tavily_request(payload: dict[str, str | int]) -> dict:
    request = urllib.request.Request(
        TAVILY_SEARCH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8", errors="replace")
    return json.loads(body)


async def web_search(query: str) -> str:
    text = query.strip()
    if not text:
        return "Веб-поиск: запрос пустой."

    config = load_config()
    if not config.tavily_api_key:
        return "Веб-поиск недоступен: не задан TAVILY_API_KEY."

    payload = {
        "api_key": config.tavily_api_key,
        "query": text,
        "max_results": 3,
        "search_depth": "basic",
    }
    try:
        data = await asyncio.to_thread(_perform_tavily_request, payload)
    except urllib.error.HTTPError:
        return "Веб-поиск временно недоступен."
    except urllib.error.URLError:
        return "Веб-поиск временно недоступен."
    except TimeoutError:
        return "Веб-поиск временно недоступен."
    except json.JSONDecodeError:
        return "Веб-поиск вернул некорректный ответ."

    results = data.get("results") or []
    if not results:
        return "По веб-поиску ничего не найдено."

    lines = ["Найдено в интернете:"]
    for idx, row in enumerate(results[:3], 1):
        title = (row.get("title") or "Без названия").strip()
        url = (row.get("url") or "URL отсутствует").strip()
        content = (row.get("content") or "").replace("\n", " ").strip()
        snippet = content[:200] + ("..." if len(content) > 200 else "")
        lines.append(f"{idx}. {title} — {url}")
        if snippet:
            lines.append(f"   {snippet}")

    return "\n".join(lines)
