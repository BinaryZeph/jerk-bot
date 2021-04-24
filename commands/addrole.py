from discord.ext import commands

class addrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addrole(self, ctx, emote, role):
        if ctx.author.guild_permissions.administrator:
            await ctx.reply('Configuring emote {}, for role *{}*'.format(emote, role))
            await ctx.message.add_reaction(emote)
        else:
            await ctx.reply('You are not authorized to run this...')

def setup(bot):
    bot.add_cog(addrole(bot))