import asyncpg
import os
from config_data.config import DATABASE_URL

DB_URL = os.getenv("DATABASE_URL")

async def get_db():
    return await asyncpg.connect(DB_URL)


async def init_db():
    conn = await get_db()

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS travels (
                       id SERIAL PRIMARY KEY,
                       user_id BIGINT,
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

async def set_user_mode(user_id: int, mode: str):
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
        UPDATE users SET current_travel = $1 WHERE user_-id = $2
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

