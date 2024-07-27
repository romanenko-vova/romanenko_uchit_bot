import aiosqlite
from romanenko_uchit_bot.static.conversions import (
    CONV_REGISTERED,
    CONV_GUIDE,
    CONV_PHONE,
    CONV_HELPER,
)


DB_PATH = "users.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                id_tg INTEGER default 0,
                status INTEGER default 0,        
                name TEXT,
                phone TEXT
            )
        """)
        await db.commit()


async def get_conversions():
    db = await aiosqlite.connect(DB_PATH)

    number_users = []
    statuses = [CONV_REGISTERED, CONV_GUIDE, CONV_PHONE, CONV_HELPER]

    for status in statuses:
        total_users_with_status = await db.execute(
            """SELECT COUNT(*) FROM users WHERE status >= ?""", (status,)
        )

        total_users_with_status = await total_users_with_status.fetchone()
        total_users_with_status = total_users_with_status[0]

        number_users.append(total_users_with_status)

    return number_users
