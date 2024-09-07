import os
from dotenv import load_dotenv
from utils.database import initialize_db
import logging

load_dotenv()
bot_token = os.getenv('BOT_TOKEN', "No token found")
bot_prefix = os.getenv('BOT_PREFIX', "!")

async def setup_hook(bot):
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