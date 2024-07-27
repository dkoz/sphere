import aiosqlite
import os

DATABASE_PATH = os.path.join('data', 'palworld.db')

async def log_ban(player_id: str, reason: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO bans (player_id, reason)
            VALUES (?, ?)
        """, (player_id, reason))
        await db.commit()