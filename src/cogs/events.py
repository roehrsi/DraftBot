from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self.bot))
        print('------')


def setup(bot):
    bot.add_cog(Events(bot))
