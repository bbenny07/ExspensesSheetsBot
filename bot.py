import logging
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import socket
import signal
from aiohttp import web
from config_data.config import TELEGRAM_TOKEN
from handlers import user_handlers
from lexicon import bot_description


bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(user_handlers.router)

async def set_bot_description(bot: Bot):
    await bot.set_my_description(
        description=bot_description.BOT_DESCRIPTION
    )

    await bot.set_my_short_description(
        short_description=bot_description.BOT_DESCRIPTION_SHORT
    ) 

# stop_event = asyncio.Event()

# async def background_loop():
#     while not stop_event.is_set():
#         # Тут может быть твоя логика
#         await asyncio.sleep(60)

# async def start():
#     await asyncio.gather(
#         dp.start_polling(bot),
#         background_loop()
#     )

# def main():
#     logging.basicConfig(level=logging.INFO)
#     loop = asyncio.get_event_loop()

#     try:
#         loop.run_until_complete(start())
#     except (KeyboardInterrupt, SystemExit):
#         logging.info("Остановка по Ctrl+C или SIGTERM")
#         stop_event.set()
#         loop.run_until_complete(bot.session.close())
#     finally:
#         loop.close()
#         logging.info("Бот остановлен.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await set_bot_description(bot)
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())