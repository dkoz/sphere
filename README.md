# Project Zero Palworld
 > [!WARNING]  
 > Still in development, use at your own risk!

 This bot is intended to be a replacement for my current [Palbot](https://github.com/dkoz/palworld-palbot) project. 

## Features:
 - **Server Management**: Ability to control your servers directly from the bot.
 - **Player Logging**: Log extensive information about players who are active on your servers.
 - **Ban List Logger**: When players are banned through the bot, it will be logged in the SQL database with the reason.
 - **Whitelist Management**: Allows you to enable a whitelist for your server so only select users can play.
 - **Administration Control**: Allows you to kick, ban, and manage players on your server directly from the bot.
 - **Server Query**: Allows you query servers added to the bot.

## Installation
 1. Create a `.env` file and fill out your `BOT_TOKEN` and `BOT_PREFIX`
 2. Run the bot with `python main.py`
 3. Use `/help` to see all available commands on the bot.

## This project runs my libaries.
 - **Palworld API Wrapper** - A python library that acts as a wrapper for the Palworld server REST API.