#main.py

import os
import logging
import discord
from discord.ext import commands
from bot import MyDiscordBot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from userdata import UserDataManager
import datetime
import pytz
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)

# Create the Discord bot instance
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize user data manager and scheduler
user_data_manager = UserDataManager('user_data.db')
scheduler = AsyncIOScheduler()

# Create instances of the command and reminder classes
my_discord_bot = MyDiscordBot(bot, user_data_manager, scheduler)

@bot.event
async def on_ready():
    logging.info(f'Bot is ready: {bot.user.name} - {bot.user.id}')
    await my_discord_bot.setup()

@bot.event
async def on_guild_available(guild):
    await my_discord_bot.register(guild)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("An error occurred while executing the command. Please try again.")
        logging.error(f"Command Error: {ctx.command} - {error}")

@bot.command()
async def help(ctx):
    # Provide a helpful message with information about available commands
    help_message = "Here is a list of available commands:\n"
    for command in bot.commands:
        help_message += f"!{command.name} : {command.help}\n"
    await ctx.send(help_message)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
