from config_data.config import SHEET_NAME, SHEET_CATEGORIES_NAME, TABLE_NAME, ADMINS_UID, DATABASE_URL
import asyncpg
import asyncio
from config_data.config import client

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

async def get_or_create_name_user_file(user_id: int, username: str) -> str:
    uid = str(user_id)
    conn = await get_db_connection()

    row = await conn.fetchrow("SELECT table_name FROM user_files WHERE user_id=$1", int(uid))
    if row:
        await conn.close()
        return row["table_name"]
    
    # если записи нет, создаём
    if uid not in ADMINS_UID:
        table_name = f"{TABLE_NAME}_{username}"
    else:
        table_name = TABLE_NAME

    await conn.execute(
        "INSERT INTO user_files(user_id, username, table_name) VALUES($1, $2, $3)",
        int(uid), username, table_name
    )
    await conn.close()
    return table_name

def get_user_categories(table):
    try:
        category_sheet = table.worksheet(SHEET_CATEGORIES_NAME)
        categories = category_sheet.col_values(1)  # Столбец A
        return [cat.strip() for cat in categories if cat.strip()]
    except Exception as e:
        return []

def find_categories_for_user(partial, table):
    all_cats = get_user_categories(table)
    return [cat for cat in all_cats if partial.lower() in cat.lower()]

def get_all_rows(table):
    # Открываем таблицу по имени или id
    sheet = table.worksheet(SHEET_NAME)
    # Получаем все строки
    rows = sheet.get_all_values()
    return rows

def edit_row_in_table(table, new_row, index):
    sheet = table.worksheet(SHEET_NAME)
    sheet.update(f"A{index+1}:D{index+1}", [new_row], value_input_option="USER_ENTERED")

def delete_row_if_empty_after_clear(table, index: int):
    sheet = table.worksheet(SHEET_NAME)

    # Очистить первые 4 ячейки
    sheet.update(f"A{index+1}:D{index+1}", [["", "", "", ""]], value_input_option="USER_ENTERED")

    row = sheet.get(f"A{index+1}:Z{index+1}")
    values = row[0] if row else []

    # Проверить, осталась ли строка пустой
    if all(cell.strip() == "" for cell in values):
        sheet.delete_rows(index + 1)
        return True  # Удалена
    return False  # Не удалена
