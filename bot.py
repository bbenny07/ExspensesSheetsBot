import logging
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from config_data.config import TELEGRAM_TOKEN, WEBHOOK_URL
from handlers import user_handlers
from lexicon import bot_description
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


# bot = Bot(
#     token=TELEGRAM_TOKEN,
#     default=DefaultBotProperties(parse_mode=ParseMode.HTML)
# )
# dp = Dispatcher(storage=MemoryStorage())
# dp.include_router(user_handlers.router)

# async def set_bot_description(bot: Bot):
#     await bot.set_my_description(
#         description=bot_description.BOT_DESCRIPTION
#     )

#     await bot.set_my_short_description(
#         short_description=bot_description.BOT_DESCRIPTION_SHORT
#     ) 

# async def main():
#     logging.basicConfig(level=logging.INFO)
#     await set_bot_description(bot)
#     await bot.delete_webhook(drop_pending_updates=False)
#     await dp.start_polling(bot)

# if __name__ == '__main__':
#     asyncio.run(main())

import os
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_PATH = "/webhook"
url = WEBHOOK_URL + WEBHOOK_PATH
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(user_handlers.router)

async def set_bot_description(bot: Bot):
    await bot.set_my_description(description=bot_description.BOT_DESCRIPTION)
    await bot.set_my_short_description(short_description=bot_description.BOT_DESCRIPTION_SHORT)

async def on_startup(app):
    logging.info("Setting webhook...")
    await set_bot_description(bot)
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    logging.info("Shutting down webhook...")
    await bot.delete_webhook()

app = web.Application()
webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=url)
# Регистрируем обработчик запросов на определенном пути

# Настраиваем приложение и связываем его с диспетчером и ботом
setup_application(app, dp, bot=bot)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))