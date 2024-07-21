import asyncio
import logging
from gamercon_async import GameRCON

async def rcon_command(server_config, server_name, command):
    server = server_config["RCON_SERVERS"].get(server_name)
    if not server:
        logging.error(f"Server not found: {server_name}")
        return "Server not found."
    async with GameRCON(server["RCON_HOST"], server["RCON_PORT"], server["RCON_PASS"]) as pc:
        try:
            return await asyncio.wait_for(pc.send(command), timeout=10.0)
        except asyncio.TimeoutError:
            logging.error(f"Command timed out: {server_name} {command}")
            return "Command timed out."
        except Exception as e:
            logging.error(f"Error sending command: {e}")
            return f"Error sending command: {e}"
