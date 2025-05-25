import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
import os

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TABLE_NAME = os.getenv('TABLE_NAME')
SHEET_NAME = os.getenv('SHEET_NAME')

# --- Авторизация в Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(TABLE_NAME).worksheet(SHEET_NAME)

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

categories = [
    "Продукты", "Кафе", "Сушка", "Химчистка", "Сушилка", "Бытовая химия",
    "Электричество+газ", "Страховка", "Связь", "Интернет",
    "Врач", "Лекарства", "Футбол", "Транспорт", "Театр",
    "Стрижка", "Музей", "Развлечения", "Французский",
    "Ютуб", "Бассейн", "Другое",
    "Путешествие", "Хвастики"
]

def find_categories(partial: str):
    partial_lower = partial.lower()
    return [cat for cat in categories if partial_lower in cat.lower()]

class Form(StatesGroup):
    waiting_for_category_choice = State()



@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
    "Привет! Отправь сообщение в формате:\n\nкатегория сумма [комментарий]\nили\nдата категория сумма [комментарий]"
)

def parse_message(msg_text: str, msg_date: datetime):
    parts = msg_text.strip().split()

    try:
        # Пробуем прочитать смещение в днях
        offset = int(parts[0])
        date = (msg_date + timedelta(days=offset)).date()
        category = parts[1].capitalize()
        amount = float(parts[2].replace('.', ','))
        comment = " ".join(parts[3:])
    except ValueError:
        # Если смещения нет — значит дата = дата сообщения
        date = msg_date.date()
        category = parts[0].capitalize()
        amount = float(parts[1].replace('.', ','))
        comment = " ".join(parts[2:])
    
    return date.strftime('%d.%m.%Y'), category, amount, comment

@dp.message()
async def handle_expense(message: Message, state: FSMContext):
    try:
        date_str, category, amount, comment = parse_message(message.text.strip(), message.date)
        matches = find_categories(category)
        if not matches:
            await message.answer("Категория не найдена, попробуйте другой ввод.")
            return
        if len(matches) == 1:
            category = matches[0]
            sheet.append_row([date_str, category, amount, comment], value_input_option="USER_ENTERED")
            await message.answer(f"✅ Добавлено: {category}, {amount} EUR, {date_str}, {comment}")
    
        else:
        # Несколько вариантов — показываем кнопки выбора
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=cat, callback_data=f"category:{cat}")]
                for cat in matches
            ]
            )
            # Сохраняем данные для последующей обработки
            await state.update_data(date_str=date_str, amount=amount, comment=comment)
            await message.answer("Найдено несколько категорий, выберите нужную:", reply_markup=keyboard)
            await state.set_state(Form.waiting_for_category_choice)
    except Exception as e:    
        await message.answer("❌ Неверный формат. Введи: `-1 кафе 300` или `кафе 300`")


@dp.callback_query(F.data.startswith("category:"), StateFilter(Form.waiting_for_category_choice))
async def process_category_choice(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":", 1)[1]
    data = await state.get_data()
    date_str = data.get("date_str")
    amount = data.get("amount")
    comment = data.get("comment")

    sheet.append_row([date_str, category, amount, comment], value_input_option="USER_ENTERED")
    await callback.message.answer(
        f"✅ Добавлено: {category}, {amount} EUR, {date_str}, {comment}"
    )
    await state.clear()
    await callback.answer()

if __name__ == '__main__':
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
