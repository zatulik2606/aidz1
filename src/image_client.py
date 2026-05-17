import base64

from openai import AsyncOpenAI

from src.config import Config


async def generate_image_reply(
    image_bytes: bytes,
    history: list[dict[str, str]],
    config: Config,
    user_hint: str = "",
) -> str:
    client = AsyncOpenAI(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
    )
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    hint_text = user_hint.strip()
    image_task_text = (
        "Проанализируй это фото аварийного события или оборудования. "
        "Если описания от пользователя нет, выполни первичный анализ самостоятельно: "
        "определи признаки неисправности, вероятные причины, предложи шаги проверки и устранения, "
        "а также выдели самый быстрый и самый эффективный способ действий. "
        "Не требуй дополнительного текста перед ответом: сначала дай best-effort разбор по фото."
    )
    if hint_text:
        image_task_text += f" Дополнительный контекст от пользователя: {hint_text}"

    image_content: list[dict[str, object]] = [
        {
            "type": "text",
            "text": image_task_text,
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
        },
    ]
    messages: list[dict[str, object]] = [
        {"role": "system", "content": config.system_prompt_image},
        *history,
        {"role": "user", "content": image_content},
    ]
    response = await client.chat.completions.create(
        model=config.llm_image_model,
        messages=messages,
    )
    content = response.choices[0].message.content
    return (content or "").strip()
