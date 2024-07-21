import aiosqlite
import os

DATABASE_PATH = "data.db"

async def db_connection():
    conn = None
    try:
        conn = await aiosqlite.connect(DATABASE_PATH)
    except aiosqlite.Error as e:
        print(e)
    return conn

async def initialize_db():
    commands = [
        """CREATE TABLE IF NOT EXISTS servers (
            guild_id INTEGER NOT NULL,
            server_name TEXT NOT NULL,
            host TEXT NOT NULL,
            password TEXT NOT NULL,
            api_port INTEGER,
            PRIMARY KEY (guild_id, server_name)
        )""",
        """CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            account_name TEXT NOT NULL,
            user_id TEXT NOT NULL,
            ip TEXT NOT NULL,
            ping REAL NOT NULL,
            location_x REAL NOT NULL,
            location_y REAL NOT NULL,
            level INTEGER NOT NULL
        )"""
    ]
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        for command in commands:
            await cursor.execute(command)
        await conn.commit()
        await conn.close()

async def add_player(player):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("""
            INSERT OR REPLACE INTO players (player_id, name, account_name, user_id, ip, ping, location_x, location_y, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player['playerId'],
            player['name'],
            player['accountName'],
            player['userId'],
            player['ip'],
            player['ping'],
            player['location_x'],
            player['location_y'],
            player['level']
        ))
        await conn.commit()
        await conn.close()

async def fetch_all_servers():
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM servers")
        servers = await cursor.fetchall()
        await conn.close()
        return servers

async def add_server(guild_id, server_name, host, password, api_port):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("INSERT INTO servers (guild_id, server_name, host, password, api_port) VALUES (?, ?, ?, ?, ?)",
                       (guild_id, server_name, host, password, api_port))
        await conn.commit()
        await conn.close()

async def fetch_server_details(guild_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("SELECT guild_id, server_name, host, password, api_port FROM servers WHERE guild_id = ? AND server_name = ?", (guild_id, server_name))
        server_details = await cursor.fetchone()
        await conn.close()
        return server_details

async def remove_server(guild_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM servers WHERE guild_id = ? AND server_name = ?", (guild_id, server_name))
        await conn.commit()
        await conn.close()

async def server_autocomplete(guild_id, current):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("SELECT server_name FROM servers WHERE guild_id = ? AND server_name LIKE ?", (guild_id, f'%{current}%'))
        servers = await cursor.fetchall()
        await conn.close()
        return [server[0] for server in servers]

if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_db())
