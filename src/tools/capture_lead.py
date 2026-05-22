async def capture_lead(name: str, contact: str, request_text: str) -> str:
    normalized_name = name.strip() or "Не указано"
    normalized_contact = contact.strip() or "Не указано"
    normalized_request = request_text.strip() or "Не указано"
    return (
        "Лид зафиксирован (тестовый режим): "
        f"имя={normalized_name}, контакт={normalized_contact}, запрос={normalized_request}"
    )
