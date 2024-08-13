import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils.whitelist import (
    add_whitelist,
    remove_whitelist,
    is_whitelisted,
    whitelist_set,
    whitelist_get
)
from utils.database import (
    fetch_all_servers,
    server_autocomplete
)
from palworld_api import PalworldAPI
import logging

class WhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_whitelist.start()

    def cog_unload(self):
        self.check_whitelist.cancel()

    # So much easier than RCON. lol
    @tasks.loop(seconds=60)
    async def check_whitelist(self):
        servers = await fetch_all_servers()
        for server in servers:
            guild_id, server_name, host, password, api_port = server
            if not await whitelist_get(guild_id, server_name):
                continue
            try:
                api = PalworldAPI(f"http://{host}:{api_port}", "admin", password)
                player_list = await api.get_player_list()
                for player in player_list['players']:
                    playerid = player['userId']
                    if not await is_whitelisted(playerid):
                        await api.kick_player(playerid, "You are not whitelisted.")
                        logging.info(f"Player {playerid} kicked from server '{server_name}' for not being whitelisted.")
                logging.info(f"Whitelist checked for server '{server_name}'.")
            except Exception as e:
                logging.error(f"An unexpected error occurred while checking whitelist for server '{server_name}': {str(e)}")

    @check_whitelist.before_loop
    async def before_check_whitelist(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="add", description="Add a player to the whitelist.")
    @app_commands.describe(playerid="The playerid of the player to whitelist.")
    @app_commands.default_permissions(administrator=True)
    async def whitelist_add(self, interaction: discord.Interaction, playerid: str):
        try:
            await add_whitelist(playerid, True)
            await interaction.response.send_message(f"Player {playerid} has been added to the whitelist.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            logging.error(f"An unexpected error occurred: {str(e)}")

    @app_commands.command(name="remove", description="Remove a player from the whitelist.")
    @app_commands.describe(playerid="The playerid of the player to remove from the whitelist.")
    @app_commands.default_permissions(administrator=True)
    async def whitelist_remove(self, interaction: discord.Interaction, playerid: str):
        try:
            await remove_whitelist(playerid)
            await interaction.response.send_message(f"Player {playerid} has been removed from the whitelist.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            logging.error(f"An unexpected error occurred: {str(e)}")

    async def server_names(self, interaction: discord.Interaction, current: str):
        guild_id = interaction.guild.id
        server_names = await server_autocomplete(guild_id, current)
        return [app_commands.Choice(name=name, value=name) for name in server_names]

    @app_commands.command(name="enable", description="Enable whitelist for a server.")
    @app_commands.describe(server_name="The name of the server to enable the whitelist for.")
    @app_commands.autocomplete(server_name=server_names)
    @app_commands.default_permissions(administrator=True)
    async def enable_whitelist(self, interaction: discord.Interaction, server_name: str):
        try:
            await whitelist_set(interaction.guild_id, server_name, True)
            await interaction.response.send_message(f"Whitelist has been enabled for server {server_name}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            logging.error(f"An unexpected error occurred: {str(e)}")

    @app_commands.command(name="disable", description="Disable whitelist for a server.")
    @app_commands.describe(server_name="The name of the server to disable the whitelist for.")
    @app_commands.autocomplete(server_name=server_names)
    @app_commands.default_permissions(administrator=True)
    async def disable_whitelist(self, interaction: discord.Interaction, server_name: str):
        try:
            await whitelist_set(interaction.guild_id, server_name, False)
            await interaction.response.send_message(f"Whitelist has been disabled for server {server_name}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            logging.error(f"An unexpected error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(WhitelistCog(bot))
