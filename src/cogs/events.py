import discord
from discord.ext import commands

from src import dicts, data


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self.bot))
        print('------')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # catch bot reaction
        channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)
        print(str(payload.emoji) == '❌', payload.user_id != self.bot.user.id)
        if (str(payload.emoji) == '❌') and (payload.user_id != self.bot.user.id):
            embed: discord.Embed = message.embeds[0]
            # check finished draft
            if embed and embed.fields[-1].value != data.FIN:
                await message.delete()
                await message.channel.send(dicts.DRAFT_RESET, delete_after=5)
        else:
            await message.remove_reaction(payload.emoji, payload.member)


def setup(bot):
    bot.add_cog(Events(bot))
