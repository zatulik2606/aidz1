from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.config import Config
from src.llm import generate_reply


def build_router(config: Config) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def handle_start(message: Message) -> None:
        await message.answer("Привет! Я запущен и готов к работе.")

    @router.message(F.text)
    async def handle_text_message(message: Message) -> None:
        user_text = message.text or ""
        answer = await generate_reply(user_text=user_text, config=config)
        await message.answer(answer or "Модель вернула пустой ответ.")

    return router
