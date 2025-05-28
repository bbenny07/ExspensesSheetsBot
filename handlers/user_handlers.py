from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from services.user_data import get_or_create_name_user_file, find_categories_for_user
from keyboards.inline_keyboards import category_selection_keyboard, add_or_rewrite_keyboard
from lexicon import messages, categories
from config_data.config import SHEET_NAME, SHEET_CATEGORIES_NAME
from services.parser_messages import parse_message
from config_data.config import client
from states.states import Form
from aiogram.filters import StateFilter

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    user_id, username = message.from_user.id, message.from_user.username
    table_name = get_or_create_name_user_file(user_id, username)
    await message.answer(messages.START.format(table_name=table_name))

@router.message()
async def handle_expense(message: Message, state: FSMContext):
    table = client.open(get_or_create_name_user_file(message.from_user.id, message.from_user.username))
    sheet = table.worksheet(SHEET_NAME)
    
    try:
        date_str, category, amount, comment = parse_message(message.text.strip(), message.date)
        matches = find_categories_for_user(category, table)
        
        if not matches:
            await state.update_data(date_str=date_str, category=category, amount=amount, comment=comment)
            keyboard = add_or_rewrite_keyboard()
            await message.answer(categories.CATEGORY_NOT_FOUND.format(category=category), reply_markup=keyboard)
            await state.set_state(Form.waiting_for_new_category_confirmation)
            return
        
        if len(matches) == 1:
            category = matches[0]
            sheet.append_row([date_str, category, amount, comment], value_input_option="USER_ENTERED")
            await message.answer(categories.ADDED_SUCCESSFULLY.format(
                category=category,
                amount=amount,
                date=date_str,
                comment=comment
            ))
        else:
            keyboard = category_selection_keyboard(matches)
            await state.update_data(date_str=date_str, amount=amount, comment=comment)
            await message.answer(categories.MULTIPLE_CATEGORIES, reply_markup=keyboard)
            await state.set_state(Form.waiting_for_category_choice)

    except Exception:
        await message.answer(messages.INVALID_FORMAT)

@router.callback_query(F.data == "add_category", StateFilter(Form.waiting_for_new_category_confirmation))
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id, username = callback.from_user.id, callback.from_user.username
    table = client.open(get_or_create_name_user_file(user_id, username))
    
    try:
        cat_sheet = table.worksheet(SHEET_CATEGORIES_NAME)
        cat_sheet.append_row([data["category"]])
        table.worksheet(SHEET_NAME).append_row([data["date_str"], data["category"], data["amount"], data["comment"]])
        await callback.message.answer(categories.CATEGORY_ADDED.format(category=data["category"]))
    except Exception as e:
        await callback.message.answer(categories.CATEGORY_ADDED_ERROR.format(error=e))
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "rewrite_message", StateFilter(Form.waiting_for_new_category_confirmation))
async def rewrite_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.REWRITE_MESSAGE)
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("category:"), StateFilter(Form.waiting_for_category_choice))
async def process_category_choice(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":", 1)[1]
    data = await state.get_data()
    date_str = data.get("date_str")
    amount = data.get("amount")
    comment = data.get("comment")

    user_id, username = callback.from_user.id, callback.from_user.username
    table = client.open(get_or_create_name_user_file(user_id, username))
    table.append_row([date_str, category, amount, comment], value_input_option="USER_ENTERED")
    await callback.message.answer(categories.ADDED_SUCCESSFULLY.format(
        category=category,
        amount=amount,
        date=date_str,
        comment=comment
    ))
    await state.clear()
    await callback.answer() 
