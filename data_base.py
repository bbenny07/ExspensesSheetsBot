import asyncpg
import os
from config_data.config import DATABASE_URL

DB_URL = os.getenv("DATABASE_URL")

async def get_db():
    return await asyncpg.connect(DB_URL)
