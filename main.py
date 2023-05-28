import discord
from discord.ext import commands
from utils import Utils
from userdata import UserDataManager
from chatgpt import ChatGPT

import os
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

user_data_manager = UserDataManager('user_data.db')

chatgpt = ChatGPT(os.getenv('YOUR_API_KEY'))

@bot.event
async def on_ready():
    logging.info(f"We have logged in as {bot.user}")

@bot.command()
async def fitnessplan(ctx):
    user_session = Utils.create_user_session(ctx.author.id)

    dm_channel = await ctx.author.create_dm()

    questions = Utils.get_questions()

    for question in questions:
        await dm_channel.send(embed=Utils.create_embed(question))

        try:
            msg = await bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, dm_channel), timeout=60.0)
            user_session[question] = msg.content
        except asyncio.TimeoutError:
            await dm_channel.send(embed=Utils.create_embed("You didn't reply in time. Please try the command again."))
            return  # Exit the command if timeout occurs

    prompt = Utils.create_prompt(user_session)

    user_data_manager.set_user_data(str(ctx.author.id), user_session)

    response = chatgpt.get_response(prompt)

    await dm_channel.send(embed=Utils.create_embed(f"Your fitness plan:\n{response}"))

@bot.command()
async def myplan(ctx):
    user_info = user_data_manager.get_user_data(str(ctx.author.id))

    dm_channel = await ctx.author.create_dm()

    if user_info:
        await dm_channel.send(embed=Utils.create_embed(f"Your fitness plan: {user_info}"))
    else:
        await dm_channel.send(embed=Utils.create_embed("You don't have a fitness plan yet. Use !fitnessplan to create one."))

@fitnessplan.error
async def fitnessplan_error(ctx, error):
    if isinstance(error, asyncio.TimeoutError):
        dm_channel = await ctx.author.create_dm()
        await dm_channel.send(embed=Utils.create_embed("Command timeout occurred. Please try again later."))

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
