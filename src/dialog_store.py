from uuid import uuid4

chat_histories: dict[int, list[dict[str, str]]] = {}
user_threads: dict[int, str] = {}


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


def start_new_thread(user_id: int) -> str:
    thread_id = f"{user_id}:{uuid4().hex[:8]}"
    user_threads[user_id] = thread_id
    return thread_id


def get_thread_id(user_id: int) -> str:
    existing = user_threads.get(user_id)
    if existing:
        return existing
    return start_new_thread(user_id)
