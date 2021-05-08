import os
from dotenv import load_dotenv
from cogwatch import Watcher
from datetime import datetime

import sqlite3
con = sqlite3.connect('bot.db')

import logging
if not os.path.exists("Logs"):
    os.makedirs("Logs")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename='Logs/jerkbot.log', filemode='w')

import discord
from discord.ext import commands, tasks

from epicstore_api import EpicGamesStoreAPI

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# Load configuration from .env file
load_dotenv()
DISCORDTOKEN = os.getenv('DISCORDTOKEN')

# Declare bot discord intents, tells discord how the bot will function
intents = discord.Intents.default()
intents.members = True

# Apply bot config from .env
bot = commands.Bot(command_prefix=os.getenv('BOTPREFIX'), intents=intents)

bot.discordguild = int(os.getenv('DISCORDGUILD'))
bot.rolemessageid = int(os.getenv('ROLEMESSAGEID'))
bot.rolechannelid = int(os.getenv('ROLECHANNELID'))
bot.freegameschannelid = int(os.getenv('FREEGAMESCHANNELID'))

@bot.event
async def on_raw_reaction_add(payload):
    # If this is not the message ID of the role message, ignore it
    if payload.message_id != bot.rolemessageid:
        return

    logging.info('Event: on_raw_reaction_add')
    
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
    logging.debug('reaction_remove called')
    
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


# Every hour, check to see if there is a new game up on the Epic Game store for free, and post it to discord
@tasks.loop(hours=1)
async def epic_free_game_check():
    
    # Set the free-games channel
    freeGamesChannel = bot.get_channel(bot.freegameschannelid)
    
    # Lookup free-games from the Epic Store API
    api = EpicGamesStoreAPI()
    free_games = api.get_free_games()['data']['Catalog']['searchStore']['elements']

    # Loop through all games in the result
    for game in free_games:
        # Confirm the game has an active promotion, we won't post past or future promos
        if game['promotions']:
            if game['promotions']['promotionalOffers']:
                game_name = game['title']
                game_description = game['description']
                game_slug = game['productSlug']
                game_url = 'https://www.epicgames.com/store/en-US/p/'+game['productSlug']
                game_price = "~~{}~~ Free".format(game['price']['totalPrice']['fmtPrice']['originalPrice'])
                
                game_thumbnail = None
                for image in game['keyImages']:
                    if image['type'] == 'Thumbnail':
                        game_thumbnail = image['url']

                promotion_data = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]
                end_date_iso = promotion_data['endDate'][:-1]
                end_date = datetime.fromisoformat(end_date_iso)
                end_date_formatted = custom_strftime('%A, %b {S}, %Y', end_date)

                # Pull additional information about the game's rating
                gameRatings = api.get_product_reviews('EPIC_'+game['productSlug'])['data']['OpenCritic']['productReviews']
                gameRatingInfo = "{} ({})".format(gameRatings['openCriticScore'], gameRatings['award'])

                # Check to see if we've already seen this free-game before
                cur = con.cursor()
                cur.execute("SELECT * FROM epicGames WHERE game=? AND end_date=?", (game_name,end_date, ))
                gameCheck = cur.fetchone()

                # If the SQL result is none, it's safe to assume we haven't seen the game before and it's okay to write to discord
                if gameCheck is None:
                    
                    # Insert the game into the epicGames table so we know we've seen it
                    cur = con.cursor()
                    cur.execute("INSERT INTO epicGames VALUES(?,?,?,?)",(game_name, game_slug, game_url, end_date))
                    con.commit()                 

                    # Post about the game to discord in the free-games channel
                    embed=discord.Embed(title="Free Game on Epic Games", url=game_url, color=0x007bff)
                    embed.set_thumbnail(url=game_thumbnail)
                    embed.add_field(name=game_name, value=game_description, inline=False)
                    embed.add_field(name="Expires", value=end_date_formatted, inline=True)
                    embed.add_field(name="Price", value=game_price, inline=True)
                    embed.add_field(name="OpenCritic Rating", value=gameRatingInfo, inline=False)
                    await freeGamesChannel.send(embed=embed)

@bot.event
async def on_ready():
    # Set the bot's status, ex. 'Playing some bot game'
    game = discord.Game("some bot game")
    await bot.change_presence(status=discord.Status.online, activity=game)

    # Initiate watcher, a package that dynamically loads all commands in a dir
    # New files and edits are hot loaded without shutting down/restarting the bot
    watcher = Watcher(bot, path="commands", preload=True)
    await watcher.start()

    epic_free_game_check.start()

    logging.info('Logged in as: %s with id: %s', bot.user.name, bot.user.id)

# Run the bot
bot.run(DISCORDTOKEN)