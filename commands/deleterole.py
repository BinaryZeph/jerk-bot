import sqlite3

from discord.ext import commands
import discord

class deleterole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def deleterole(self, ctx, newrole):
        # deleterole: Deletes a given role and emoji to the db, and adds the emoji to the role post to listen to
        # Flow: get role, get emoji, write to db, add emoji to post, acknowledge the command post

        print('\n\n-------------')
        print('deleterole called')
        
        # Fetch guild information 
        guild = discord.Client.get_guild(self.bot, id=self.bot.discordguild)

        # Confirm that the person who is sending the message has admin permissions in the guild
        guildMember = await guild.fetch_member(ctx.author.id)
        if not guildMember.guild_permissions.administrator:
            return

        # Fetch Role information from the Guild
        role = discord.utils.get(guild.roles,name=newrole)

        # Write the role, role ID, emoji, and emoji ID to the database
        con = sqlite3.connect('bot.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM roles WHERE role=?",(newrole,))
        
        roleDetail = cur.fetchone()

        # Fetch Emoji information from the Guild
        guildemoji = discord.utils.get(guild.emojis,name=roleDetail[2])

        # Add a reaction to the role post
        roleChannel = self.bot.get_channel(self.bot.rolechannelid)
        roleMessage = await roleChannel.fetch_message(self.bot.rolemessageid)
        await roleMessage.clear_reaction(guildemoji)

        cur.execute("DELETE FROM roles WHERE roleid=?",(roleDetail[1],))
        con.commit()

        # Acknowledge the command by checking it off
        await ctx.message.add_reaction(emoji='✅')

def setup(bot):
    bot.add_cog(deleterole(bot))