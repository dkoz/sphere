import discord
from discord.ext import commands, tasks
from utils.database import add_player, fetch_all_servers
from palworld_api import PalworldAPI
import logging

class PlayerLoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_players.start()

    def cog_unload(self):
        self.log_players.cancel()

    @tasks.loop(seconds=30)
    async def log_players(self):
        servers = await fetch_all_servers()
        for server in servers:
            guild_id, server_name, host, password, api_port = server
            try:
                api = PalworldAPI(f"http://{host}:{api_port}", "admin", password)
                player_list = await api.get_player_list()
                for player in player_list['players']:
                    await add_player(player)
                logging.info(f"Players from server '{server_name}' logged successfully.")
            except Exception as e:
                logging.error(f"An unexpected error occurred while logging players from server '{server_name}': {str(e)}")

    @log_players.before_loop
    async def before_log_players(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(PlayerLoggingCog(bot))
