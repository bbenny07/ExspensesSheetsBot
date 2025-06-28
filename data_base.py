import asyncpg
import os
from config_data.config import DATABASE_URL

DB_URL = os.getenv("DATABASE_URL")

async def get_db():
    return await asyncpg.connect(DB_URL)


async def init_db():
    conn = await get_db()
    await conn.execute('SET search_path TO public;')
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS travels (
                       id SERIAL PRIMARY KEY,
                       user_id BIGINT,
                       file_id TEXT NOT NULL,
                       title TEXT,
                       is_active BOOLEAN DEFAULT TRUE
                       );
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
                       user_id BIGINT PRIMARY KEY,
                       mode TEXT DEFAULT 'normal',
                       current_travel TEXT
                       );
""")
    await conn.close()

async def set_user_mode(user_id: int, mode: str='normal'):
    conn = await get_db()
    await conn.execute("""
        INSERT INTO users (user_id, mode)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE SET mode =$2
    """, user_id, mode)
    await conn.close()

async def get_user_mode(user_id: int) -> str:
    conn = await get_db()
    row = await conn.fetchrow("SELECT mode FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return row["mode"] if row else 'normal'

async def set_current_travel(user_id: int, travel_title:str):
    conn = await get_db()
    await conn.execute("""
        UPDATE users SET current_travel = $1 WHERE user_id = $2
""", travel_title, user_id)
    await conn.close()

async def get_current_travel(user_id: int) -> str | None:
    conn = await get_db()
    row = await conn.fetchrow("SELECT current_travel FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return row["current_travel"] if row else None

async def clear_current_travel(user_id: int):
    conn = await get_db()
    await conn.execute("UPDATE users SET current_travel = NULL WHERE user_id = $1", user_id)
    await conn.close()

async def add_travel(user_id: int, title: str):
    conn = await get_db()
    row = await conn.fetchrow("SELECT table_name FROM user_files WHERE user_id = $1", user_id)
    file_id = row["table_name"]
    await conn.execute("""
        INSERT INTO travels (user_id, title, is_active, file_id) VALUES ($1, $2, TRUE, $3)
    """, user_id, title, file_id)
    await conn.close()

async def get_active_travels(user_id: int) -> list[str]:
    conn = await get_db()
    row = await conn.fetchrow("SELECT table_name FROM user_files WHERE user_id = $1", user_id)
    file_id = row["table_name"]
    rows = await conn.fetch("""
        SELECT title FROM travels WHERE file_id = $1 AND is_active = TRUE
    """, file_id)
    await conn.close()
    return [row["title"] for row in rows]

async def end_travel(user_id: int, title: str):
    conn = await get_db()
    await conn.execute("""
        UPDATE travels SET is_active = FALSE WHERE user_id = $1 AND title = $2
    """, user_id, title)
    await conn.close()