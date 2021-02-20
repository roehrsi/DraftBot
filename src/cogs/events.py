from discord.ext import commands

from src import dicts


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self.bot))
        print('------')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (reaction.emoji == "❌") and (user.id != self.bot.user.id):
            await reaction.message.delete()
            await reaction.message.channel.send(dicts.DRAFT_RESET, delete_after=5)


def setup(bot):
    bot.add_cog(Events(bot))
