import sqlite3
import re

from discord.ext import commands
import discord

class addrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addrole(self, ctx, newrole, emoji):
        # addrole: Adds a given role and emoji to the db, and adds the emoji to the role post to listen to
        # Flow: get role, get emoji, write to db, add emoji to post, acknowledge the command post

        print('\n\n-------------')
        print('addRole called')
        
        # Fetch guild information 
        guild = discord.Client.get_guild(self.bot, id=self.bot.discordguild)

        # Confirm that the person who is sending the message has admin permissions in the guild
        guildMember = await guild.fetch_member(ctx.author.id)
        if not guildMember.guild_permissions.administrator:
            return

        # Fetch Role information from the Guild
        role = discord.utils.get(guild.roles,name=newrole)

        # Confirm the role exists
        if newrole != role.name:
            await ctx.reply('Role was not found in the server')
            return

        # Parse the emoji supplied in the message to get it's raw name and ID
        # Sample: <a:beeAngry:835918192680763422> (optional a, denotes animation)
        emojiFormat=r"<a?:(?P<name>[\w]+):(?P<id>[0-9]+)>"
        emojiDetail=re.search(emojiFormat,emoji)
        emojiId = int(emojiDetail.group('id'))
        emojiName = emojiDetail.group('name')

        # Fetch Emoji information from the Guild
        guildemoji = discord.utils.get(guild.emojis,name=emojiName)

        # Confirm the emoji is in the guild
        if emojiId != guildemoji.id:
            await ctx.reply('Emoji not found in guild, emoji must be ')
            return

        # Write the role, role ID, emoji, and emoji ID to the database
        con = sqlite3.connect('bot.db')
        cur = con.cursor()
        cur.execute("INSERT INTO roles VALUES(?,?,?,?)",(role.name, role.id, emojiName, emojiId))
        con.commit()

        # Add a reaction to the role post
        roleChannel = self.bot.get_channel(self.bot.rolechannelid)
        roleMessage = await roleChannel.fetch_message(self.bot.rolemessageid)
        await roleMessage.add_reaction(emoji)

        # Acknowledge the command by checking it off
        await ctx.message.add_reaction(emoji='✅')

def setup(bot):
    bot.add_cog(addrole(bot))