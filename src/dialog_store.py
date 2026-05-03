chat_histories: dict[int, list[dict[str, str]]] = {}


def get_history(chat_id: int) -> list[dict[str, str]]:
    return chat_histories.get(chat_id, [])


def add_user_message(chat_id: int, text: str) -> None:
    chat_histories.setdefault(chat_id, []).append(
        {"role": "user", "content": text}
    )


def add_assistant_message(chat_id: int, text: str) -> None:
    chat_histories.setdefault(chat_id, []).append(
        {"role": "assistant", "content": text}
    )


def clear_history(chat_id: int) -> None:
    chat_histories.pop(chat_id, None)
