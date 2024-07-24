import aiosqlite
import os

DATABASE_PATH = os.path.join('data', 'palworld.db')

async def log_ban(steam_id: str, reason: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO bans (steam_id, reason)
            VALUES (?, ?)
        """, (steam_id, reason))
        await db.commit()