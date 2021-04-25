from discord.ext import commands

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def react(self, ctx, emote):
        roleChannel = self.bot.get_channel(786601265522147388)
        roleMessage = await roleChannel.fetch_message(786601366487433236)
        await roleMessage.add_reaction(emote)

        # Acknowledge the command by checking it off, then delete it a few seconds later
        await ctx.message.add_reaction(emoji='✅')
        


def setup(bot):
    bot.add_cog(React(bot))