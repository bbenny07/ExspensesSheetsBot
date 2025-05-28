import json
import os
from config_data.config import SHEET_CATEGORIES_NAME, USER_FILES_JSON, TABLE_NAME, ADMINS_UID

def load_user_files():
    if os.path.exists(USER_FILES_JSON):
        with open(USER_FILES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_files(data):
    with open(USER_FILES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_files = load_user_files()

def get_or_create_name_user_file(user_id, username):
    uid = str(user_id)
    if uid not in user_files:
        if uid not in ADMINS_UID:
            user_files[uid] = f"{TABLE_NAME} {username}"
            save_user_files(user_files)
        else:
            user_files[uid] = TABLE_NAME
            save_user_files(user_files)
    return user_files[uid]

def get_user_categories(table):
    try:
        category_sheet = table.worksheet(SHEET_CATEGORIES_NAME)
        categories = category_sheet.col_values(1)  # Столбец A
        return [cat.strip() for cat in categories if cat.strip()]
    except Exception as e:
        print(f"Ошибка при чтении категорий: {e}")
        return []

def find_categories_for_user(partial, table):
    all_cats = get_user_categories(table)
    return [cat for cat in all_cats if partial.lower() in cat.lower()]
