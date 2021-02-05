from random import randint
from discord.ext import commands
from src.data import *
from src.util import isin


class DraftCog(commands.Cog, name="DraftCog"):
    def __init__(self, bot):
        self.bot = bot
        self.currentDraft = None

    @commands.group()
    async def draft(self, ctx):
        if self.currentDraft is None:
            self.currentDraft = Draft(None, None)
        if ctx.invoked_subcommand is None:
            s = "Welcome to the draft, {0}!\n".format(ctx.author.mention)
            s += "If you want to draft a map, type ``!draft tournament`` to start the coin flip and draft a map.\n"
            s += "Otherwise use ``!draft quick [map]`` to skip map draft and pick a map directly, then do the coin flip.\n"
            s += "If you want to restart the draft, simply call this base command again to reset all parameters."
            await ctx.send(s)

    @draft.command()
    async def tournament(self, ctx):
        coin = randint(0, 1)
        if coin == 1:
            self.currentDraft.teamFirst = Team(captain=ctx.author, map_pick="-")
            self.currentDraft.teamSecond = Team(captain="Opponent")
            s = "You won the coin toss. Your opponent will start banning a map now by typing ``!ban map."
        else:
            pass  # todo

    @draft.command()
    async def quick(self, ctx, arg):
        if arg is not None:
            match = isin(arg, "maps")
            if match:
                self.currentDraft.teamSecond = Team(captain=ctx.author, map_bans=["-", "-"], map_pick=match)
                self.currentDraft.teamFirst = Team(captain="Opponent", map_bans=["-", "-"], map_pick="-")
                self.currentDraft.stage_num = 5
                s = "{0} picked {1}!".format(self.currentDraft.teamSecond.captain,
                                             self.currentDraft.teamSecond.map_pick)
                s += "Please start banning two heroes each by writing ``!ban hero [hero]``. Opponent goes first!"
            else:
                s = "I couldn't find a map with that name :(\n"
                s += "Maybe try again with a different map."
            await ctx.send(s)

    @commands.command()
    async def ban(self, ctx, arg):
        bans = isin(arg, "maps")
        if bans is None:
            bans = isin(arg, "heroes")
            if bans is None:
                s = "I could not find a map or hero with that name."
                await ctx.send(s)
                return
        await self.lock(ctx, picks=bans)

    @commands.command()
    async def pick(self, ctx, **args):
        bans = isin(args, "maps")
        if bans is None:
            bans = isin(args, "heroes")
            if bans is None:
                s = "I could not find a map or hero with that name."
                await ctx.send(s)
                return
        await self.lock(ctx, picks=bans)

    async def lock(self, ctx: commands.context, picks=None):
        draft: Draft = self.currentDraft
        if draft is None:
            await self.reset_draft()
        if picks:
            # ban maps
            if draft.stage_num in draft.second_map_bans:
                draft.teamSecond.map_bans.append(picks[0])
                draft.stage_num += 1
            if draft.stage_num in draft.first_map_bans:
                draft.teamFirst.map_bans.append((picks[0]))
                draft.stage_num += 1
            # pick map
            if draft.stage_num == draft.second_map_pick:
                draft.teamSecond.map_pick = picks[0]
                draft.stage_num += 1
            # ban heroes
            if draft.stage_num in draft.first_hero_bans:
                draft.teamFirst.hero_bans.append(picks[0])
                draft.stage_num += 1
            if draft.stage_num in draft.second_hero_bans:
                draft.teamSecond.hero_bans.append(picks[0])
                draft.stage_num += 1
            # pick heroes
            if draft.stage_num in draft.first_hero_picks:
                for pick in picks[:1]:
                    draft.teamFirst.hero_picks.append(pick)
                    draft.stage_num += 1
            if draft.stage_num in draft.second_hero_picks:
                for pick in picks[:1]:
                    draft.teamSecond.hero_picks.append(pick)
                    draft.stage_num += 1

    async def reset_draft(self):
        self.currentDraft = Draft()

    async def print_draft(self):
        pass


def setup(bot):
    bot.add_cog(DraftCog(bot))
