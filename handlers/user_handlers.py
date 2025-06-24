from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from services.user_data import get_or_create_name_user_file, find_closest_category, find_categories_for_user, get_user_categories, get_all_rows, edit_row_in_table, delete_row_if_empty_after_clear
from keyboards.inline_keyboards import  (
    get_travel_mode_keyboard, get_delete_travel_confirmation_keyboard,
    get_enter_new_travel_keyboard, get_choose_travel_keyboard, get_row_edit_cancel_keyboard,
    get_cancelled_action_keyboard, category_selection_keyboard, add_or_rewrite_keyboard, 
    get_feedback_menu_keyboard, get_cancel_feedback_keyboard, get_row_navigation_keyboard, 
    get_delete_confirmation_keyboard)
from keyboards.main_menu import get_main_menu_keybord
from lexicon import messages, categories, commands, buttons
from config_data.config import SHEET_NAME, SHEET_CATEGORIES_NAME, ADMIN_UID, EMAIL_AGENT
from services.parser_messages import parse_message, convert_data_datetime
from services.pick_phrases import pick_phrase
from config_data.config import client, N_ROW_TEXT, N_COLUMN
from states.states import *
from aiogram.filters import StateFilter
import random
import data_base

router = Router()

async def get_table(user_id: int, username: str):
    table_name = await get_or_create_name_user_file(user_id, username)
    table = client.open(table_name)
    return table

def format_row(row: list) -> str:
    return " | ".join(f"{cell}" for cell in row[:N_COLUMN])

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    keyboard = get_main_menu_keybord()
    table_name = await get_or_create_name_user_file(message.from_user.id, message.from_user.username)
    await message.answer(messages.START.format(table_name=table_name, email=EMAIL_AGENT), reply_markup=keyboard)

@router.message(F.text == buttons.TRAVEL_EXPENSE)
async def change_mode_travel(message: Message):
    await data_base.set_user_mode(message.from_user.id, mode=buttons.MODES[message.text])
    text = messages.TRAVEL_MODE_ENTERED + "\n\n"
    current_travel = await data_base.get_current_travel(message.from_user.id)
    travels = await data_base.get_active_travels(message.from_user.id)
    if current_travel:
        text += messages.CURRENT_TRAVEL.format(name=current_travel)
    else:
        text += messages.TRAVEL_NOT_SELECTED

    keyboard = get_choose_travel_keyboard(travels, current_travel)
    await message.answer(text, reply_markup=keyboard)

@router.message(StateFilter(TravelState.waiting_for_new_travel))
async def add_new_travel(message: Message, state: FSMContext):
    await state.clear()
    new_acive_travel = message.text
    await data_base.add_travel(message.from_user.id, new_acive_travel)
    await data_base.set_current_travel(message.from_user.id, new_acive_travel)
    keyboard = get_travel_mode_keyboard(new_acive_travel)
    await message.answer(text=messages.TRAVEL_ADDED.format(name=new_acive_travel), reply_markup=keyboard)

@router.message(F.text == buttons.USUAL_EXPENSE)
async def change_mode_usual(message: Message):
    await data_base.set_user_mode(message.from_user.id, mode=buttons.MODES[message.text])
    await message.answer(text=messages.USUAL_EXPENSE_MODE)

@router.callback_query(F.data == 'new_travel')
async def add_new_travel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TravelState.waiting_for_new_travel)
    text = messages.TRAVEL_MODE_ENTERED + "\n\n"
    text += messages.ENTER_NEW_TRAVEL_TEXT
    await callback.message.edit_text(text=text, keyboard=get_enter_new_travel_keyboard())

@router.callback_query(F.data == 'travel_mode')
async def add_new_travel(callback: CallbackQuery, state: FSMContext):    
    await data_base.set_user_mode(callback.from_user.id, mode=buttons.MODES[callback.message.text])
    text = messages.TRAVEL_MODE_ENTERED + "\n\n"
    current_travel = await data_base.get_current_travel(callback.from_user.id)
    travels = await data_base.get_active_travels(callback.from_user.id)
    if current_travel:
        text += messages.CURRENT_TRAVEL.format(name=current_travel)
    else:
        text += messages.TRAVEL_NOT_SELECTED

    keyboard = get_choose_travel_keyboard(travels, current_travel)
    await callback.message.edit_text(text, reply_markup=keyboard)
    # await state.clear()

@router.callback_query(F.data == 'exit_travel_mode')
async def exit_travel_mode(callback: CallbackQuery, state: FSMContext):
    await data_base.set_user_mode(callback.from_user.id)
    await callback.message.answer(messages.EXITED_TRAVEL_MODE)
    # await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("clear_travel:"))
async def end_active_travel(callback: CallbackQuery):
    current_travel = callback.data.split(':')[1]
    keyboard = get_delete_travel_confirmation_keyboard(current_travel)
    text = messages.CONFIRM_DELETE_TRAVEL.format(name=current_travel)
    await callback.message.edit_text(text=text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("confirm_delete_travel:"))
async def delete_active_travel(callback: CallbackQuery):
    current_travel = callback.data.split(':')[1]
    text = messages.TRAVEL_ENDED.format(name=current_travel)
    await data_base.end_travel(callback.from_user.id, current_travel)
    await data_base.clear_current_travel(callback.from_user.id)
    travels = await data_base.get_active_travels(callback.from_user.id)
    text = "\n\n" + messages.TRAVEL_MODE_ENTERED + "\n\n" + messages.TRAVEL_NOT_SELECTED
    keyboard = get_choose_travel_keyboard(travels, current_travel)
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("cancel_delete_travel:"))
async def cancel_delete_active_travel(callback: CallbackQuery):
    text = messages.TRAVEL_MODE_ENTERED + "\n\n"
    current_travel = callback.data.split(':')[1]
    travels = await data_base.get_active_travels(callback.from_user.id)
    text += messages.CURRENT_TRAVEL.format(name=current_travel)
    keyboard = get_choose_travel_keyboard(travels, current_travel)
    await callback.message.edit_text(text=text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("travel:"))
async def start_current_travel_mode(callback: CallbackQuery):
    current_travel = callback.data.split(':')[1]
    await data_base.set_current_travel(callback.from_user.id, current_travel)
    text = messages.TRAVEL_MODE_ENTERED + "\n\n"
    text += messages.CURRENT_TRAVEL.format(name=current_travel)
    travels = await data_base.get_active_travels(callback.from_user.id)
    keyboard = get_choose_travel_keyboard(travels, current_travel)
    if callback.message.text != text:
        await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await callback.answer()

@router.message(Command('categories'))
async def show_categories(message: Message, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(message.from_user.id, message.from_user.username)
        await state.update_data(table=table)
    categories_list = get_user_categories(table)
    categories_text = "\n".join(f"• {cat}" for cat in categories_list)
    await message.answer(categories.CATEGORIES_LIST.format(categories_text=categories_text))

@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(commands.COMMANDS_RESPONSES[message.text])

@router.message(Command('table'))
async def show_table(message: Message, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(message.from_user.id, message.from_user.username)
        await state.update_data(table=table)
    rows = await get_all_rows(table, message.from_user.id)
    current_row = rows[-1][:N_COLUMN]
    total_rows = len(rows)
    current_index = total_rows - 1
    await state.update_data(rows=rows)
    await message.answer(commands.COMMANDS_RESPONSES[message.text].format(last_line=format_row(current_row)),
                         reply_markup=get_row_navigation_keyboard(current_index, total_rows))

@router.callback_query(F.data.startswith("row_"))
async def show_table_back(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(callback.from_user.id, callback.from_user.username)
        await state.update_data(table=table)
    rows = await get_all_rows(table, callback.from_user.id)
    index = min(index, len(rows) - 1)
    current_row = rows[index][:N_COLUMN]
    total_rows = len(rows)
    await state.update_data(rows=rows)
    await callback.message.edit_text(messages.CURRENT_ROW.format(index=index+1,current_row=format_row(current_row)),
                         reply_markup=get_row_navigation_keyboard(index, total_rows))

@router.callback_query(F.data.startswith("delete_"))
async def confirm_delete_prompt(callback: CallbackQuery, state:FSMContext):
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(callback.from_user.id, callback.from_user.username)
        await state.update_data(table=table)
    rows = await get_all_rows(table, callback.from_user.id)
    total_rows = len(rows)
    if index > total_rows - 1:
        current_row = rows[-1][:N_COLUMN]
        await callback.message.edit_text(
        messages.FAILED_TO_OPEN_ROW.format(current_row=format_row(current_row)),
        reply_markup=get_row_navigation_keyboard(total_rows - 1, total_rows)
        )
        return
    current_row = rows[index][:N_COLUMN]
    await callback.message.edit_text(
        messages.CONFIRM_DELETE_ROW_MESSAGE.format(index=index+1, current_row=format_row(current_row)),
        reply_markup=get_delete_confirmation_keyboard(index)
    )

@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[2])
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(callback.from_user.id, callback.from_user.username)
        await state.update_data(table=table)
    rows = await get_all_rows(table, callback.from_user.id)
    total_rows = len(rows)
    if index > total_rows - 1:
        current_row = rows[-1][:N_COLUMN]
        await callback.message.edit_text(
        messages.FAILED_TO_OPEN_ROW.format(current_row=format_row(current_row)),
        reply_markup=get_row_navigation_keyboard(total_rows - 1, total_rows)
        )
        return
    current_row = rows[index][:N_COLUMN]
    if await delete_row_if_empty_after_clear(table, index, callback.from_user.id):
        text = messages.ROW_DELETE_SUCCESS_MESSAGE.format(index=index+1, current_row=format_row(current_row))
    else:
        text = messages.PART_ROW_DELETE_SUCCESS_MESSAGE.format(index=index+1, current_row=format_row(current_row))
    await callback.message.edit_text(
        text=text,
        reply_markup=get_row_navigation_keyboard(index, len(rows))
    )
    rows = await get_all_rows(table, callback.from_user.id)
    await state.update_data(rows=rows)

@router.callback_query(F.data.startswith("cancel_delete_"))
async def cancel_delete(callback: CallbackQuery):
    index = int(callback.data.split("_")[2])
    await callback.message.edit_text(text=messages.DELETE_ROW_CANCELLED, reply_markup=get_cancelled_action_keyboard(index))

@router.callback_query(F.data.startswith(("edit_")))
async def edit_rows(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(callback.from_user.id, callback.from_user.username)
        await state.update_data(table=table)
    index = int(callback.data.split("_")[1])
    rows = await get_all_rows(table, callback.from_user.id)
    total_rows = len(rows)
    if index > total_rows - 1:
        current_row = rows[-1][:N_COLUMN]
        await callback.message.edit_text(
        messages.FAILED_TO_OPEN_ROW.format(current_row=format_row(current_row)),
        reply_markup=get_row_navigation_keyboard(total_rows - 1, total_rows)
        )
        return
    current_row = rows[index][:(N_COLUMN- 1)]
    await state.update_data(index=index, table=table, current_row=current_row)
    await callback.message.answer(
        text=messages.EDIT_ROW_PROMPT.format(index=index+1, current_row=" ".join(current_row)),
        reply_markup=get_row_edit_cancel_keyboard(index)
    )
    await state.set_state(EditRowState.waiting_for_edit_row)
    await callback.answer()

@router.callback_query(F.data.startswith("cancel_edit_"))
async def cancel_edit_row(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    await callback.message.delete()
    # index = int(callback.data.split("_")[2])
    # await callback.message.edit_text(text=messages.EDIT_ROW_CANCELLED, reply_markup=get_cancelled_action_keyboard(index))
    await state.clear()
    await state.up_data(table=table)

@router.callback_query(F.data == "close_view")
async def close_view_handler(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception as e:
        await callback.answer(messages.FAILED_TO_DELETE_MESSAGE)
    else:
        await callback.answer()

@router.message(EditRowState.waiting_for_edit_row)
async def handle_full_row_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    row = data.get('current_row')
    index = data.get('index')
    try:
        date_str, category, amount, comment = parse_message(
                                message.text.strip(), 
                                convert_data_datetime(row[0]))
        matches = find_categories_for_user(category, table)
        if not matches:
            await state.update_data(date_str=date_str, category=category, amount=amount, comment=comment)
            close_matches = await find_closest_category(category, table)
            keyboard = add_or_rewrite_keyboard(categories=close_matches)
            await message.answer(
                categories.CATEGORY_NOT_FOUND.format(category=category),
                reply_markup=keyboard
            )
            await state.set_state(EditRowState.waiting_for_edit_category_confirmation)
            return
        if len(matches) == 1:
            category = matches[0]
            new_row = [date_str, category, amount, comment]
            await edit_row_in_table(table, new_row, index, message.from_user.id)
            await message.answer(messages.EDIT_ROW_SUCCESSFULLY.format(current_row=format_row(new_row)), 
                                 reply_markup=get_cancelled_action_keyboard(index))
        else:
            keyboard = category_selection_keyboard(matches)
            await state.update_data(date_str=date_str, amount=amount, comment=comment)
            await message.answer(categories.MULTIPLE_CATEGORIES, reply_markup=keyboard)
            await state.set_state(EditRowState.waiting_for_edit_category_choice)
            return

    except Exception as e:
        print(date_str, category, amount, comment, e)
        await message.answer(messages.INVALID_FORMAT)
    await state.clear()

@router.callback_query(F.data == "rewrite_message", StateFilter(EditRowState.waiting_for_edit_category_confirmation))
async def rewrite_edit_message(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_row = data.get('current_row')
    index = data.get('index')
    table = data.get('table')
    await callback.message.answer(messages.REWRITE_MESSAGE)
    await state.clear()
    await state.set_state(EditRowState.waiting_for_edit_row)
    await state.update_data(index=index, current_row=current_row, table=table)
    await callback.answer()

@router.callback_query(F.data.startswith("category:"), StateFilter(EditRowState.waiting_for_edit_category_choice))
async def process_edit_category_choice(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":", 1)[1]
    data = await state.get_data()
    date_str = data.get("date_str")
    amount = data.get("amount")
    comment = data.get("comment")
    index = data.get("index")

    table = data.get('table')
    new_row = [date_str, category, amount, comment]
    await edit_row_in_table(table, new_row, index, callback.from_user.id)
    await callback.message.answer(messages.EDIT_ROW_SUCCESSFULLY.format(current_row=format_row(new_row)),
                                  reply_markup=get_cancelled_action_keyboard(index))
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith(("next_", "prev_")))
async def navigate_rows(callback: CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)
    data = await state.get_data()
    index = int(callback.data.split('_')[1])
    rows = data.get('rows')
    if rows is None:
        table = data.get('table')
        if table is None:
            table = await get_table(callback.from_user.id, callback.from_user.username)
        rows = await get_all_rows(table, callback.from_user.id)
        await state.update_data(rows=rows, table=table)
    if callback.data.startswith("next_"):
        index = min(index + 1, len(rows) - 1)
    else:
        index = max(N_ROW_TEXT, index - 1)
        index = min(index, len(rows) - 1)
    row = rows[index]
    new_text = messages.CURRENT_ROW.format(index=index+1, current_row=format_row(row))
    if callback.message.text != new_text:
        await callback.message.edit_text(text=new_text,
                                        reply_markup=get_row_navigation_keyboard(index, len(rows)))
    await callback.answer()

@router.message(Command('feedback'))
async def feedback_command(message: Message, state: FSMContext):
    await message.answer(commands.COMMANDS_RESPONSES[message.text],
                         reply_markup=get_feedback_menu_keyboard())
    
@router.callback_query(F.data == 'start_feedback')
async def ask_feedback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.FEEDBACK_WAIT,
                                  reply_markup=get_cancel_feedback_keyboard())
    await state.set_state(Form.waiting_for_feedback)
    await callback.answer()

@router.message(StateFilter(Form.waiting_for_feedback))
async def receive_feedback(message: Message, state: FSMContext):
    feedback = message.text
    user = message.from_user

    text_to_admin = messages.FEEDBACK_FOR_ADMIN.format(
    user_id=user.id,
    username=user.username or 'Без username',
    message=feedback
    )
    await message.bot.send_message(chat_id=ADMIN_UID, text=text_to_admin)
    await message.answer(messages.FEEDBACK_SENT)
    await state.clear()

@router.callback_query(F.data == "cancel_feedback")
async def cancel_feedback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.FEEDBACK_CANCEL)
    await state.clear()
    await callback.answer()

@router.message()
async def handle_expense(message: Message, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(message.from_user.id, message.from_user.username)
    mode = await data_base.get_user_mode(message.from_user.id) 
    mode = mode if mode else 'normal'
    current_travel = await data_base.get_current_travel(message.from_user.id) if mode == "travel" else ""
    sheet = table.worksheet(SHEET_NAME[mode])
    try:
        date_str, category, amount, comment = parse_message(message.text.strip(), message.date)
        matches = find_categories_for_user(category, table)

        if not matches:
            await state.update_data(date_str=date_str, category=category, amount=amount, comment=comment)
            close_matches = await find_closest_category(category, table)
            keyboard = add_or_rewrite_keyboard(categories=close_matches)
            await message.answer(
                categories.CATEGORY_NOT_FOUND.format(category=category),
                reply_markup=keyboard
            )
            await state.set_state(Form.waiting_for_new_category_confirmation)
            return

        if len(matches) == 1:
            category = matches[0]
            sheet.append_row([date_str, category, amount, comment, current_travel], value_input_option="USER_ENTERED")
            # phrase = random.choice(categories.SUPPORT_PHRASES)
            phrase = pick_phrase(date_str, category, amount, comment, table)
            # reply_kb = get_travel_mode_keyboard(current_travel) if mode == "travel" else None
            await message.answer(categories.ADDED_SUCCESSFULLY.format(
                current_row=format_row([date_str, category, amount, comment, current_travel]),
                phrase=phrase
            ))
            rows = await get_all_rows(table, message.from_user.id)
            await state.update_data(rows=rows)
        else:
            keyboard = category_selection_keyboard(matches)
            await state.update_data(date_str=date_str, amount=amount, comment=comment)
            await message.answer(categories.MULTIPLE_CATEGORIES, reply_markup=keyboard)
            await state.set_state(Form.waiting_for_category_choice)

    except Exception as e:
        await message.answer(messages.INVALID_FORMAT)
  

@router.callback_query(F.data == "add_category", StateFilter(Form.waiting_for_new_category_confirmation))
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(callback.from_user.id, callback.from_user.username)
    
    try:
        cat_sheet = table.worksheet(SHEET_CATEGORIES_NAME)
        cat_sheet.append_row([data["category"]])
        mode = await data_base.get_user_mode(callback.from_user.id) 
        mode = mode if mode else 'normal'
        current_travel = await data_base.get_current_travel(callback.from_user.id) if mode == "travel" else ""
        sheet = table.worksheet(SHEET_NAME[mode])
        sheet.append_row([data["date_str"], data["category"], data["amount"], data["comment"], current_travel])
        await callback.message.answer(categories.CATEGORY_ADDED.format(category=data["category"], 
                                                                       date=data["date_str"], 
                                                                       amount=data["amount"], comment=data["comment"]))
    except Exception as e:
        await callback.message.answer(categories.CATEGORY_ADDED_ERROR.format(error=e))
    
    await state.clear()
    rows = await get_all_rows(table, callback.from_user.id)
    await state.update_data(rows=rows)
    await callback.answer()

@router.callback_query(F.data == "rewrite_message", StateFilter(Form.waiting_for_new_category_confirmation))
async def rewrite_message(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    table = data.get('table')
    if table is None:
        table = await get_table(callback.from_user.id, callback.from_user.username)
    await callback.message.answer(messages.REWRITE_MESSAGE)
    await state.clear()
    await state.update_data(table=table)
    await callback.answer()

@router.callback_query(F.data.startswith("category:"), 
                       StateFilter(Form.waiting_for_category_choice, Form.waiting_for_new_category_confirmation))
async def process_category_choice(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":", 1)[1]
    data = await state.get_data()
    date_str = data.get("date_str")
    amount = data.get("amount")
    comment = data.get("comment")

    table = data.get('table')
    if table is None:
        table = await get_table(callback.from_user.id, callback.from_user.username)
    mode = await data_base.get_user_mode(callback.from_user.id)
    mode = mode if mode else 'normal'
    current_travel = await data_base.get_current_travel(callback.from_user.id) if mode == "travel" else ""
    sheet = table.worksheet(SHEET_NAME[mode])
    sheet.append_row([date_str, category, amount, comment, current_travel], value_input_option="USER_ENTERED")
    # phrase = random.choice(categories.SUPPORT_PHRASES)
    phrase = pick_phrase(date_str, category, amount, comment, table)
    # reply_kb = get_travel_mode_keyboard(current_travel) if mode == "travel" else None
    await callback.message.answer(categories.ADDED_SUCCESSFULLY.format(
        current_row=format_row([date_str, category, amount, comment, current_travel]),
        phrase=phrase
    ))
    await state.clear()
    rows = await get_all_rows(table, callback.from_user.id)
    await state.update_data(rows=rows)
    await callback.answer() 

