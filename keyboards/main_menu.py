from lexicon import commands
from aiogram.types import BotCommand
from aiogram import Bot

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in commands.COMMANDS_INFO.items()
    ]
    await bot.set_my_commands(main_menu_commands)