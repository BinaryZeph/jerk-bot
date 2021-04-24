import os
from dotenv import load_dotenv
from cogwatch import Watcher

import sqlite3
conn = sqlite3.connect('db.sqlite')

import discord
from discord.ext import commands

# Load configuration from .env file
load_dotenv()
DISCORDTOKEN = os.getenv('DISCORDTOKEN')
DISCORDGUILD = os.getenv('DISCORDGUILD')
ROLEMESSAGEID = os.getenv('ROLEMESSAGEID')
ROLECHANNELID = os.getenv('ROLECHANNELID')
BOTPREFIX = os.getenv('BOTPREFIX')

bot = commands.Bot(BOTPREFIX)

@bot.event
async def on_raw_reaction_add(payload):
    print(payload)

@bot.event
async def on_raw_reaction_remove(payload):
    print(payload)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    game = discord.Game("some bot game")
    await bot.change_presence(status=discord.Status.online, activity=game)

    watcher = Watcher(bot, path="commands", preload=True)
    await watcher.start()

    channel = bot.get_channel(ROLECHANNELID)
    print(channel)

bot.run(DISCORDTOKEN)