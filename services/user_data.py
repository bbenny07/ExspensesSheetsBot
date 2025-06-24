from config_data.config import SHEET_NAME, SHEET_CATEGORIES_NAME, TABLE_NAME, ADMINS_UID, DATABASE_URL
import asyncpg
import asyncio
from config_data.config import client
from rapidfuzz import process, fuzz
import data_base
from sentence_transformers import SentenceTransformer, util

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

model = SentenceTransformer("intfloat/multilingual-e5-base")

def encode_e5(texts: list[str], is_query: bool = False):
    prefix = "query: " if is_query else "passage: "
    return model.encode([prefix + t.lower() for t in texts], convert_to_tensor=True)

def find_similar_category(category: str, all_categories: list[str], top_k: int = 3) -> list[str]:
    if not all_categories:
        return []

    input_embedding = encode_e5([category], is_query=True)
    category_embeddings = encode_e5(all_categories, is_query=False)

    cosine_scores = util.pytorch_cos_sim(input_embedding, category_embeddings)[0]
    top_indices = cosine_scores.topk(k=min(top_k, len(all_categories))).indices.tolist()
    return [all_categories[i] for i in top_indices]

def find_closest_category(category:str, table) -> list[str]:
    all_cats = get_user_categories(table)
    matches = process.extract(category, all_cats, scorer=fuzz.partial_ratio, processor=str.lower, score_cutoff=70)
    matches = [cat[0] for cat in matches]
    matches.extend(find_similar_category(category, all_cats))
    return list(set(matches))

def find_categories_for_user(partial, table):
    all_cats = get_user_categories(table)
    return [cat for cat in all_cats if partial.lower() in cat.lower()]

async def get_all_rows(table, user_id: int):
    mode = await data_base.get_user_mode(user_id)
    sheet_name = SHEET_NAME[mode]
    sheet = table.worksheet(sheet_name)
    rows = sheet.get_all_values()
    return rows

async def edit_row_in_table(table, new_row, index, user_id: int):
    mode = await data_base.get_user_mode(user_id)
    sheet_name = SHEET_NAME[mode]
    sheet = table.worksheet(sheet_name)
    sheet.update(f"A{index+1}:D{index+1}", [new_row], value_input_option="USER_ENTERED")

async def delete_row_if_empty_after_clear(table, index: int, user_id: int):
    mode = await data_base.get_user_mode(user_id)
    sheet_name = SHEET_NAME[mode]
    sheet = table.worksheet(sheet_name)

    # Очистить первые 4 ячейки
    sheet.update(f"A{index+1}:E{index+1}", [["", "", "", "", ""]], value_input_option="USER_ENTERED")

    row = sheet.get(f"A{index+1}:Z{index+1}")
    values = row[0] if row else []

    # Проверить, осталась ли строка пустой
    if all(cell.strip() == "" for cell in values):
        sheet.delete_rows(index + 1)
        return True
    return False

