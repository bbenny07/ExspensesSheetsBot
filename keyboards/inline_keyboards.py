from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from lexicon import buttons
from config_data.config import N_ROW_TEXT

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

def get_feedback_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons.WRITE, callback_data="start_feedback")],
        [InlineKeyboardButton(text=buttons.CANCEL, callback_data="cancel_feedback")]
    ])

def get_cancel_feedback_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons.CANCEL, callback_data="cancel_feedback")]
    ])
    return keyboard

def get_row_navigation_keyboard(current_index: int, total_rows: int) -> InlineKeyboardMarkup:
    buts = []

    nav_buttons = []
    if current_index > N_ROW_TEXT + 1:
        nav_buttons.append(
            InlineKeyboardButton(text=buttons.NAV_PREV, callback_data=f"prev_{current_index}")
        )
    if current_index < total_rows - 1:
        nav_buttons.append(
            InlineKeyboardButton(text=buttons.NAV_NEXT, callback_data=f"next_{current_index}")
        )
    if nav_buttons:
        buts.append(nav_buttons)

    buts.append([
        InlineKeyboardButton(text=buttons.EDIT_ROW, callback_data=f"edit_{current_index}"),
        InlineKeyboardButton(text=buttons.DELETE_ROW, callback_data=f"delete_{current_index}")
    ])

    buts.append([
        InlineKeyboardButton(text=buttons.CLOSE_VIEW, callback_data="close_view")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buts)

def get_delete_confirmation_keyboard(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=buttons.CONFIRM_DELETE, callback_data=f"confirm_delete_{index}"),
            InlineKeyboardButton(text=buttons.CANCEL, callback_data=f"cancel_delete_{index}")
        ]
    ])

def get_cancelled_action_keyboard(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons.BACK, callback_data=f"row_{index}")],
        [InlineKeyboardButton(text=buttons.EDIT_ROW, callback_data=f"edit_{index}")],
        [InlineKeyboardButton(text=buttons.DELETE_ROW, callback_data=f"delete_{index}")]
    ])

def get_row_edit_cancel_keyboard(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=buttons.CANCEL, callback_data="cancel_edit_{index}")]
    ])
