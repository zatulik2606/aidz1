import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.config import Config
from src.dialog_store import (
    add_assistant_message,
    add_user_message,
    clear_history,
    get_history,
)
from src.llm import generate_reply


logger = logging.getLogger(__name__)


def build_router(config: Config) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def handle_start(message: Message) -> None:
        await message.answer(
            "👋 Привет! Я ассистент инженера мониторинга.\n\n"
            "Опишите аварийное событие или алерт — я помогу:\n"
            "• классифицировать инцидент\n"
            "• определить вероятные причины\n"
            "• предложить шаги по локализации\n\n"
            "Команды:\n"
            "/reset — очистить контекст текущего инцидента"
        )

    @router.message(Command("reset"))
    async def handle_reset(message: Message) -> None:
        clear_history(message.chat.id)
        await message.answer("Контекст диалога очищен.")

    @router.message(F.text)
    async def handle_text_message(message: Message) -> None:
        chat_id = message.chat.id
        user_text = message.text or ""
        history = get_history(chat_id)
        try:
            answer = await generate_reply(
                user_text=user_text,
                history=history,
                config=config,
            )
        except Exception:
            logger.exception("LLM request failed")
            await message.answer("Сервис временно недоступен, попробуйте позже.")
            return

        add_user_message(chat_id, user_text)
        add_assistant_message(chat_id, answer)
        await message.answer(answer or "Модель вернула пустой ответ.")

    return router
