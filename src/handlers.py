import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from openai import APIStatusError

from bot.agent import run_agent
from src.config import Config
from src.dialog_store import (
    add_assistant_message,
    add_user_message,
    clear_history,
    get_history,
    get_thread_id,
    start_new_thread,
)
from src.audio_client import generate_audio_reply, _normalize_audio_format
from src.image_client import generate_image_reply
from src.telegram_text import sanitize_telegram_text


logger = logging.getLogger(__name__)


def build_router(config: Config) -> Router:
    router = Router()

    async def _handle_image_payload(
        message: Message,
        image_bytes: bytes,
        user_hint: str,
        preferred_mime: str = "",
    ) -> None:
        chat_id = message.chat.id
        history = get_history(chat_id)
        try:
            answer = await generate_image_reply(
                image_bytes=image_bytes,
                history=history,
                config=config,
                user_hint=user_hint,
                preferred_mime=preferred_mime,
            )
        except Exception:
            logger.exception("Image analysis request failed")
            await message.answer("Сервис временно недоступен, попробуйте позже.")
            return

        add_user_message(chat_id, f"[image] {user_hint}".strip())
        add_assistant_message(chat_id, answer)
        await message.answer(answer or "Не удалось сформировать ответ по изображению.")

    @router.message(CommandStart())
    async def handle_start(message: Message) -> None:
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else chat_id
        clear_history(chat_id)
        start_new_thread(user_id)
        await message.answer(
            "👋 Привет! Я Шустрый — старший инженер мониторинга ИТ-сети.\n\n"
            "Для анализа отправь текстом:\n"
            "1) что произошло,\n"
            "2) какие симптомы,\n"
            "3) какие сервисы затронуты.\n\n"
            "Или отправь фото, изображение файлом, либо голосовое сообщение.\n\n"
            "Я верну структурированный разбор и отдельно выделю:\n"
            "• самый быстрый способ устранения\n"
            "• самый эффективный способ устранения\n\n"
            "Команда:\n"
            "/reset — очистить контекст текущего инцидента"
        )

    @router.message(Command("reset"))
    async def handle_reset(message: Message) -> None:
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else chat_id
        clear_history(chat_id)
        start_new_thread(user_id)
        await message.answer("Контекст диалога очищен.")

    @router.message(F.text)
    async def handle_text_message(message: Message) -> None:
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else chat_id
        user_text = message.text or ""
        history = get_history(chat_id)
        thread_id = get_thread_id(user_id)
        try:
            answer = await run_agent(
                history=[
                    *history,
                    {"role": "user", "content": user_text, "chat_id": chat_id},
                ],
                config=config,
                thread_id=thread_id,
            )
        except Exception:
            logger.exception("LLM request failed")
            await message.answer("Сервис временно недоступен, попробуйте позже.")
            return

        safe_answer = sanitize_telegram_text(answer)
        add_user_message(chat_id, user_text)
        add_assistant_message(chat_id, safe_answer)
        await message.answer(safe_answer or "Модель вернула пустой ответ.")

    @router.message(F.photo)
    async def handle_photo_message(message: Message) -> None:
        photo = message.photo[-1]
        user_hint = message.caption or ""
        file = await message.bot.get_file(photo.file_id)
        if not file.file_path:
            await message.answer("Не удалось получить файл изображения, попробуйте снова.")
            return

        image_stream = await message.bot.download_file(file.file_path)
        image_bytes = image_stream.read()
        if not image_bytes:
            await message.answer("Не удалось прочитать изображение, попробуйте снова.")
            return

        await _handle_image_payload(
            message=message,
            image_bytes=image_bytes,
            user_hint=user_hint,
            preferred_mime="",
        )

    @router.message(F.document & F.document.mime_type.startswith("image/"))
    async def handle_image_document_message(message: Message) -> None:
        document = message.document
        if document is None:
            await message.answer("Не удалось обработать файл изображения.")
            return

        user_hint = message.caption or ""
        file = await message.bot.get_file(document.file_id)
        if not file.file_path:
            await message.answer("Не удалось получить файл изображения, попробуйте снова.")
            return

        image_stream = await message.bot.download_file(file.file_path)
        image_bytes = image_stream.read()
        if not image_bytes:
            await message.answer("Не удалось прочитать изображение, попробуйте снова.")
            return

        await _handle_image_payload(
            message=message,
            image_bytes=image_bytes,
            user_hint=user_hint,
            preferred_mime=document.mime_type or "",
        )

    @router.message(F.voice)
    async def handle_voice_message(message: Message) -> None:
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else chat_id
        history = get_history(chat_id)
        thread_id = get_thread_id(user_id)
        voice = message.voice
        if voice is None:
            await message.answer("Не удалось обработать голосовое сообщение.")
            return

        user_hint = message.caption or ""
        file = await message.bot.get_file(voice.file_id)
        if not file.file_path:
            await message.answer("Не удалось получить файл голосового сообщения.")
            return

        audio_stream = await message.bot.download_file(file.file_path)
        audio_bytes = audio_stream.read()
        if not audio_bytes:
            await message.answer("Не удалось прочитать голосовое сообщение.")
            return

        audio_format = _normalize_audio_format(voice.mime_type or "")
        try:
            transcript = await generate_audio_reply(
                audio_bytes=audio_bytes,
                config=config,
                audio_format=audio_format,
            )
            voice_text = transcript
            if user_hint:
                voice_text = f"{user_hint}\n\nТранскрипция голосового сообщения:\n{transcript}"
            answer = await run_agent(
                history=[
                    *history,
                    {"role": "user", "content": voice_text, "chat_id": chat_id},
                ],
                config=config,
                thread_id=thread_id,
            )
        except APIStatusError as error:
            if error.status_code == 402:
                await message.answer(
                    "Для обработки аудио необходимо пополнить баланс провайдера. "
                    f"Текущая модель аудио: `{config.llm_transcribe_model}`."
                )
                return
            logger.exception("Audio analysis request failed")
            await message.answer("Сервис временно недоступен, попробуйте позже.")
            return
        except Exception:
            logger.exception("Audio analysis request failed")
            await message.answer("Сервис временно недоступен, попробуйте позже.")
            return

        safe_answer = sanitize_telegram_text(answer)
        add_user_message(chat_id, f"[voice] {transcript}".strip())
        add_assistant_message(chat_id, safe_answer)
        await message.answer(
            safe_answer or "Не удалось сформировать ответ по голосовому сообщению."
        )

    return router
