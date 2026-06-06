import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from src.config import load_config
from src.handlers import build_router
from src.venv_guard import ensure_virtualenv


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


async def run() -> None:
    ensure_virtualenv()
    setup_logging()
    config = load_config()
    bot = Bot(token=config.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router(config))
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
