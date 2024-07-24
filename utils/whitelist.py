import aiosqlite
import os

DATABASE_PATH = os.path.join('data', 'palworld.db')

async def add_whitelist(steamid: str, whitelisted: bool):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO whitelist (steamid, whitelisted)
            VALUES (?, ?)
        """, (steamid, whitelisted))
        await db.commit()

async def remove_whitelist(steamid: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM whitelist WHERE steamid = ?", (steamid,))
        await db.commit()

async def is_whitelisted(steamid: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT whitelisted FROM whitelist WHERE steamid = ?", (steamid,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        return False

async def whitelist_set(guild_id: int, server_name: str, enabled: bool):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO whitelist_status (guild_id, server_name, enabled)
            VALUES (?, ?, ?)
        """, (guild_id, server_name, enabled))
        await db.commit()

async def whitelist_get(guild_id: int, server_name: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT enabled FROM whitelist_status WHERE guild_id = ? AND server_name = ?", (guild_id, server_name))
        result = await cursor.fetchone()
        if result:
            return result[0]
        return False
