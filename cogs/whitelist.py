import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils.database import add_whitelist, remove_whitelist, is_whitelisted, fetch_all_servers
from palworld_api import PalworldAPI
import logging

class WhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_whitelist.start()

    def cog_unload(self):
        self.check_whitelist.cancel()

    @tasks.loop(seconds=60)
    async def check_whitelist(self):
        servers = await fetch_all_servers()
        for server in servers:
            guild_id, server_name, host, password, api_port = server
            try:
                api = PalworldAPI(f"http://{host}:{api_port}", "admin", password)
                player_list = await api.get_player_list()
                for player in player_list['players']:
                    steamid = player['userId']
                    if not await is_whitelisted(steamid):
                        await api.kick_player(steamid, "You are not whitelisted.")
                        logging.error(f"Player {steamid} kicked from server '{server_name}' for not being whitelisted.")
                logging.error(f"Whitelist checked for server '{server_name}'.")
            except Exception as e:
                logging.error(f"An unexpected error occurred while checking whitelist for server '{server_name}': {str(e)}")

    @check_whitelist.before_loop
    async def before_check_whitelist(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="add", description="Add a player to the whitelist.")
    @app_commands.describe(steamid="The Steam ID of the player to whitelist.")
    @app_commands.default_permissions(administrator=True)
    async def whitelist_add(self, interaction: discord.Interaction, steamid: str):
        try:
            await add_whitelist(steamid, True)
            await interaction.response.send_message(f"Player {steamid} has been added to the whitelist.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            logging.error(f"An unexpected error occurred: {str(e)}")

    @app_commands.command(name="remove", description="Remove a player from the whitelist.")
    @app_commands.describe(steamid="The Steam ID of the player to remove from the whitelist.")
    @app_commands.default_permissions(administrator=True)
    async def whitelist_remove(self, interaction: discord.Interaction, steamid: str):
        try:
            await remove_whitelist(steamid)
            await interaction.response.send_message(f"Player {steamid} has been removed from the whitelist.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            logging.error(f"An unexpected error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(WhitelistCog(bot))
