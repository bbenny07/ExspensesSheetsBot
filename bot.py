import logging
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from config_data.config import TELEGRAM_TOKEN
from handlers import user_handlers
from lexicon import bot_description
from keyboards.main_menu import set_main_menu
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from keep_alive import keep_alive
keep_alive()

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

async def main():
    logging.basicConfig(level=logging.INFO)
    await set_bot_description(bot)
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
