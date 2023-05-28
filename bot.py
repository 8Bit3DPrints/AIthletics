#bot.py

from commands import Commands
from userdata import UserDataManager
import logging
from discord.ext import commands

class MyDiscordBot:
    def __init__(self, bot, user_data_manager, scheduler):
        self.bot = bot
        self.user_data_manager = user_data_manager
        self.commands = Commands(self.bot, self.user_data_manager, scheduler)

    async def setup(self):
        self.commands.register()
