from src.leads import save_lead


async def capture_lead(
    name: str,
    contact: str,
    request_text: str,
    source_chat_id: int | None = None,
    leads_db_path: str = "./data/leads.db",
) -> str:
    normalized_name = name.strip() or "Не указано"
    normalized_contact = contact.strip() or "Не указано"
    normalized_request = request_text.strip() or "Не указано"
    save_lead(
        name=normalized_name,
        contact=normalized_contact,
        request_text=normalized_request,
        source_chat_id=source_chat_id,
        leads_db_path=leads_db_path,
    )

    return (
        "Заявка сохранена. "
        f"Имя: {normalized_name}; контакт: {normalized_contact}."
    )
