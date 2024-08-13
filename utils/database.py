import aiosqlite
import os

DATABASE_PATH = os.path.join('data', 'palworld.db')

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
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            account_name TEXT NOT NULL,
            player_id TEXT NOT NULL,
            ip TEXT NOT NULL,
            ping REAL NOT NULL,
            location_x REAL NOT NULL,
            location_y REAL NOT NULL,
            level INTEGER NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS whitelist (
            player_id TEXT PRIMARY KEY,
            whitelisted BOOLEAN NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS whitelist_status (
            guild_id INTEGER NOT NULL,
            server_name TEXT NOT NULL,
            enabled BOOLEAN NOT NULL,
            PRIMARY KEY (guild_id, server_name)
        )""",
        """CREATE TABLE IF NOT EXISTS bans (
            player_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS server_logs (
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            server_name TEXT NOT NULL,
            PRIMARY KEY (guild_id, server_name)
        )""",
        """CREATE TABLE IF NOT EXISTS query_logs (
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            server_name TEXT NOT NULL,
            message_id INTEGER NOT NULL,
            player_message_id INTEGER NOT NULL,
            PRIMARY KEY (guild_id, server_name)
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
            INSERT OR REPLACE INTO players (user_id, name, account_name, player_id, ip, ping, location_x, location_y, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player['userId'],
            player['name'],
            player['accountName'],
            player['playerId'],
            player['ip'],
            player['ping'],
            player['location_x'],
            player['location_y'],
            player['level']
        ))
        await conn.commit()
        await conn.close()

async def fetch_player(user_id):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        player = await cursor.fetchone()
        await conn.close()
        return player

async def player_autocomplete(current):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("SELECT user_id, name FROM players WHERE name LIKE ?", (f'%{current}%',))
        players = await cursor.fetchall()
        await conn.close()
        return [(player[0], player[1]) for player in players]

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

async def remove_whitelist_status(guild_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM whitelist_status WHERE guild_id = ? AND server_name = ?", (guild_id, server_name))
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
    
# Server Logs
async def add_logchannel(guild_id, channel_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("""
            INSERT OR REPLACE INTO server_logs (guild_id, channel_id, server_name)
            VALUES (?, ?, ?)
        """, (guild_id, channel_id, server_name))
        await conn.commit()
        await conn.close()

async def remove_logchannel(guild_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM server_logs WHERE guild_id = ? AND server_name = ?", (guild_id, server_name))
        await conn.commit()
        await conn.close()

async def fetch_logchannel(guild_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("SELECT channel_id FROM server_logs WHERE guild_id = ? AND server_name = ?", (guild_id, server_name))
        result = await cursor.fetchone()
        await conn.close()
        return result[0] if result else None
    
# Query Server
async def add_query(guild_id, channel_id, server_name, message_id, player_message_id):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("""
            INSERT OR REPLACE INTO query_logs (guild_id, channel_id, server_name, message_id, player_message_id)
            VALUES (?, ?, ?, ?, ?)
        """, (guild_id, channel_id, server_name, message_id, player_message_id))
        await conn.commit()
        await conn.close()

async def fetch_query(guild_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("""
            SELECT channel_id, message_id, player_message_id
            FROM query_logs
            WHERE guild_id = ? AND server_name = ?
        """, (guild_id, server_name))
        result = await cursor.fetchone()
        await conn.close()
        return result if result else None

async def delete_query(guild_id, server_name):
    conn = await db_connection()
    if conn is not None:
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM query_logs WHERE guild_id = ? AND server_name = ?", (guild_id, server_name))
        await conn.commit()
        await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_db())
