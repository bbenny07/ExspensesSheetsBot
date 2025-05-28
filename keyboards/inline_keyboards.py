from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from lexicon import buttons

def add_or_rewrite_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons.ADD_CATEGORY, callback_data="add_category")],
        [InlineKeyboardButton(text=buttons.REWRITE_MESSAGE, callback_data="rewrite_message")]
    ])
    return keyboard

def category_selection_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"category:{cat}")] for cat in categories
    ])
    return keyboard
