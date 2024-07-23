import discord
from discord.ext import commands
import settings
import os
import logging
from utils.database import initialize_db

log_path = os.path.join('logs', 'bot.log')

logging.basicConfig(level=logging.INFO, filename=log_path, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=settings.bot_prefix, intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

async def setup_hook():
    await initialize_db()
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            extension = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                logging.info(f"Loaded {extension}.")
            except Exception as e:
                logging.error(f"Failed to load {extension}: {e}")
    await bot.tree.sync()

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Palworld"))

# These are commands for development purposes only
@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Loaded {extension} successfully.")
    except Exception as e:
        await ctx.send(f"Failed to load {extension}. {type(e).__name__}: {e}")

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unloaded {extension} successfully.")
    except Exception as e:
        await ctx.send(f"Failed to unload {extension}. {type(e).__name__}: {e}")

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Reloaded {extension} successfully.")
    except Exception as e:
        await ctx.send(f"Failed to reload {extension}. {type(e).__name__}: {e}")

if __name__ == '__main__':
    bot.run(settings.bot_token)