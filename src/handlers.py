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
from src.image_client import generate_image_reply
from src.llm import generate_reply


logger = logging.getLogger(__name__)


def build_router(config: Config) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def handle_start(message: Message) -> None:
        await message.answer(
            "👋 Привет! Я старший инженер мониторинга ИТ-сети.\n\n"
            "Для анализа отправь текстом:\n"
            "1) что произошло,\n"
            "2) какие симптомы,\n"
            "3) какие сервисы затронуты.\n\n"
            "Я верну структурированный разбор и отдельно выделю:\n"
            "• самый быстрый способ устранения\n"
            "• самый эффективный способ устранения\n\n"
            "Команда:\n"
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

    @router.message(F.photo)
    async def handle_photo_message(message: Message) -> None:
        chat_id = message.chat.id
        history = get_history(chat_id)
        photo = message.photo[-1]
        user_hint = message.caption or ""
        file = await message.bot.get_file(photo.file_id)
        image_stream = await message.bot.download_file(file.file_path)
        image_bytes = image_stream.read()
        try:
            answer = await generate_image_reply(
                image_bytes=image_bytes,
                history=history,
                config=config,
                user_hint=user_hint,
            )
        except Exception:
            logger.exception("Image analysis request failed")
            await message.answer("Сервис временно недоступен, попробуйте позже.")
            return

        add_user_message(chat_id, f"[image] {user_hint}".strip())
        add_assistant_message(chat_id, answer)
        await message.answer(answer or "Не удалось сформировать ответ по изображению.")

    return router
