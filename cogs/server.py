from discord.ext import commands
from discord import app_commands
import discord
from utils.database import add_server, remove_server, server_autocomplete
from utils.servermodal import AddServerModal

class ServerManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addserver", description="Add a server configuration")
    @app_commands.default_permissions(administrator=True)
    async def add_server_command(self, interaction: discord.Interaction):
        modal = AddServerModal(title="Add Server")

        async def on_submit_override(modal_interaction: discord.Interaction):
            await modal_interaction.response.defer(ephemeral=True)

            server_name = modal.children[0].value
            host = modal.children[1].value
            rcon_port = int(modal.children[2].value)
            password = modal.children[3].value
            api_port = int(modal.children[4].value) if modal.children[4].value else None

            success = await add_server(
                interaction.guild_id,
                server_name,
                host,
                rcon_port,
                password,
                api_port
            )

            if success:
                await modal_interaction.followup.send("Server added successfully.", ephemeral=True)
            else:
                await modal_interaction.followup.send("Failed to add server.", ephemeral=True)

        modal.on_submit = on_submit_override
        await interaction.response.send_modal(modal)
        
    async def server_names(self, interaction: discord.Interaction, current: str):
        guild_id = interaction.guild.id
        server_names = await server_autocomplete(guild_id, current)
        return [app_commands.Choice(name=name, value=name) for name in server_names]

    @app_commands.command(name="removeserver", description="Remove a server configuration")
    @app_commands.autocomplete(server=server_names)
    @app_commands.default_permissions(administrator=True)
    async def remove_server_command(self, interaction: discord.Interaction, server: str):
        success = await remove_server(interaction.guild_id, server)
        if success:
            await interaction.response.send_message("Server removed successfully.")
        else:
            await interaction.response.send_message("Failed to remove server.")

async def setup(bot):
    await bot.add_cog(ServerManagementCog(bot))
