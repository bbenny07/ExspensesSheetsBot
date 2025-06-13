from lexicon import commands, buttons
from aiogram.types import BotCommand, KeyboardButton, ReplyKeyboardMarkup
from aiogram import Bot

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in commands.COMMANDS_INFO.items()
    ]
    await bot.set_my_commands(main_menu_commands)

def get_main_menu_keybord():
    main_menu = ReplyKeyboardMarkup(resize_keyboard=True,
                                    one_time_keyboard=False,
    keyboard=[
        [KeyboardButton(text=buttons.USUAL_EXPENSE)],
        [KeyboardButton(text=buttons.TRAVEL_EXPENSE)]
    ])
    return main_menu