from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.config import Config
from src.dialog_store import (
    add_assistant_message,
    add_user_message,
    get_history,
)
from src.llm import generate_reply


def build_router(config: Config) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def handle_start(message: Message) -> None:
        await message.answer("Привет! Я запущен и готов к работе.")

    @router.message(F.text)
    async def handle_text_message(message: Message) -> None:
        chat_id = message.chat.id
        user_text = message.text or ""
        history = get_history(chat_id)
        answer = await generate_reply(
            user_text=user_text,
            history=history,
            config=config,
        )
        add_user_message(chat_id, user_text)
        add_assistant_message(chat_id, answer)
        await message.answer(answer or "Модель вернула пустой ответ.")

    return router
