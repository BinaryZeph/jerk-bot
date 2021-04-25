import os
from dotenv import load_dotenv
from cogwatch import Watcher

import sqlite3
con = sqlite3.connect('bot.db')

import discord
from discord.ext import commands

# Load configuration from .env file
load_dotenv()
DISCORDTOKEN = os.getenv('DISCORDTOKEN')

# Apply bot config from .env
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=os.getenv('BOTPREFIX'), intents=intents)

bot.discordguild = int(os.getenv('DISCORDGUILD'))
bot.rolemessageid = int(os.getenv('ROLEMESSAGEID'))
bot.rolechannelid = int(os.getenv('ROLECHANNELID'))

@bot.event
async def on_raw_reaction_add(payload):
    # If this is not the message ID of the role message, ignore it
    if payload.message_id != bot.rolemessageid:
        return

    print('\n\n-------------')
    print('reaction_add called')
    
    emojiid = int(payload.emoji.id)
    userid = int(payload.user_id)

    cur = con.cursor()
    cur.execute("SELECT * FROM roles WHERE emojiid=?", (emojiid,))
    roleDetail = cur.fetchone()
    roleToAssign = int(roleDetail[1])

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
            # Check if we're still in the guild and it's cached.
            print('no guild')
            return

    role = guild.get_role(roleToAssign)
    if role is None:
            # Make sure the role still exists and is valid.
            print('no role')
            return

    member = await guild.fetch_member(userid)
    if member is None:
        # Make sure the member still exists and is valid.
        print('no member')
        return

    await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    # If this is not the message ID of the role message, ignore it
    if payload.message_id != bot.rolemessageid:
        return

    print('\n\n-------------')
    print('reaction_remove called')
    
    emojiid = int(payload.emoji.id)
    userid = int(payload.user_id)

    cur = con.cursor()
    cur.execute("SELECT * FROM roles WHERE emojiid=?", (emojiid,))
    roleDetail = cur.fetchone()
    roleToAssign = int(roleDetail[1])

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
            # Check if we're still in the guild and it's cached.
            print('no guild')
            return

    role = guild.get_role(roleToAssign)
    if role is None:
            # Make sure the role still exists and is valid.
            print('no role')
            return

    member = await guild.fetch_member(userid)
    if member is None:
        # Make sure the member still exists and is valid.
        print('no member')
        return

    await member.remove_roles(role)

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

bot.run(DISCORDTOKEN)