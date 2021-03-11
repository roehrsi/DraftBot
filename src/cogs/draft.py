import json
from random import randint

import discord
from discord.ext import commands

from src import dicts
from src.data import *
from src.util import isin

DELAY = 10
DELETE_DRAFT_EMOJI = "❌"


class DraftCog(commands.Cog, name="DraftCog"):
    def __init__(self, bot):
        self.bot = bot
        self.currentDraft = None
        self.embed = None

    with open("config.json", "r") as file:
        jfile = json.load(file)
        VERBOSE = jfile["verbose"]

    async def status_verbose(self, ctx):
        if self.VERBOSE:
            if self.currentDraft.stage_num == 4:
                await ctx.send(
                    f"{self.currentDraft.team_second.captain} can now ``!pick`` a map from the remaining pool.",
                    delete_after=DELAY)
            if self.currentDraft.stage_num == 5:
                await ctx.send(
                    f"{self.currentDraft.team_second.captain} picked **{self.currentDraft.team_second.map_pick}**!\n"
                    f"Please start banning two heroes each by writing ``!ban [hero]``. {self.currentDraft.team_first.captain} goes first!",
                    delete_after=DELAY)
            if self.currentDraft.stage_num == 9:
                await ctx.send(f"{self.currentDraft.team_first.captain} has the first pick!", delete_after=DELAY)
            if self.currentDraft.stage_num == 14:
                await ctx.send(f"{self.currentDraft.team_second.captain} bans another hero next!", delete_after=DELAY)
            if self.currentDraft.stage_num == 16:
                await ctx.send(f"{self.currentDraft.team_second.captain} continues picking!", delete_after=DELAY)
            # if self.currentDraft.stage_num == 21:
            # self.currentDraft = None

    def print_embed(self):
        draft = self.currentDraft
        embed = discord.Embed(title="Draft:", color=0xff8040)
        embed.add_field(name=draft.team_first.captain, value=repr(draft.team_first),
                        inline=True)
        embed.add_field(name=draft.team_second.captain, value=repr(draft.team_second),
                        inline=True)
        embed.add_field(name="Status:", value=draft.status(), inline=False)
        return embed

    async def update_embed(self):
        if self.embed is not None:
            await self.embed.edit(embed=self.print_embed())

    @staticmethod
    def greeting(ctx):
        return dicts.GREETING.format(ctx.author.mention)

    @commands.group()
    async def draft(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send(self.greeting(ctx), delete_after=20)

    @draft.command()
    async def tournament(self, ctx, member: discord.Member):
        self.currentDraft = Draft()
        coin = randint(0, 1)
        if coin == 1:
            self.currentDraft.team_first = Team(captain=ctx.author.name)
            self.currentDraft.team_second = Team(captain=member.name)
            s = f"{self.currentDraft.team_first.captain} won the coin toss! {self.currentDraft.team_second.captain} can start ``!ban``ning a map now."
        else:
            self.currentDraft.team_first = Team(captain=member.name)
            self.currentDraft.team_second = Team(captain=ctx.author.name)
            s = f"{self.currentDraft.team_first.captain} won the coin toss! {self.currentDraft.team_second.captain} starts ``!ban``ning a map."
        self.embed = await ctx.send(embed=self.print_embed())
        await self.embed.add_reaction(DELETE_DRAFT_EMOJI)
        await ctx.send(s, delete_after=DELAY)

    @draft.command()
    async def quick(self, ctx, arg, member: discord.Member):
        self.currentDraft = Draft()
        kind = "map"
        match = isin(kind, arg)
        if match:
            self.currentDraft.team_second = Team(captain=ctx.author.name, map_bans=["-", "-"], map_pick=match[0])
            self.currentDraft.team_first = Team(captain=member.name, map_bans=["-", "-"])
            # set the stage to 5 (hero bans)
            self.currentDraft.stage_num = 5
            self.embed = await ctx.send(embed=self.print_embed())
            await self.embed.add_reaction(DELETE_DRAFT_EMOJI)
            await ctx.send(
                f"{self.currentDraft.team_second.captain} picked **{self.currentDraft.team_second.map_pick}**!\n "
                f"Please start banning two heroes each by writing ``!ban [hero]``. {self.currentDraft.team_first.captain} goes first!",
                delete_after=DELAY)
        else:
            await ctx.send(dicts.NO_MATCH.format(kind), delete_after=DELAY)

    @commands.command()
    async def ban(self, ctx, arg):
        await ctx.message.delete()
        if self.currentDraft is None:
            await ctx.send(dicts.NO_DRAFT, delete_after=DELAY)
        else:
            if (ctx.author.name == self.currentDraft.team_first.captain and self.currentDraft.turn() == 1) or (
                    ctx.author.name == self.currentDraft.team_second.captain and self.currentDraft.turn() == 0):
                kind = "map" if self.currentDraft.stage_num <= 4 else "hero"
                bans = isin(kind, arg)
                if not bans:
                    await ctx.send(dicts.NO_MATCH.format(kind), delete_after=DELAY)
                # lock in the ban
                else:
                    # check bans for duplicates
                    if any(ban in (self.currentDraft.team_first.map_bans
                                   + self.currentDraft.team_second.map_bans
                                   + self.currentDraft.team_first.hero_bans
                                   + self.currentDraft.team_second.hero_bans) for ban in bans):
                        await ctx.send(dicts.REDUNDANT_PICK.format(kind), delete_after=DELAY)
                    else:
                        self.currentDraft.lock(bans)
                        await self.status_verbose(ctx)
        await self.update_embed()

    @commands.command()
    async def pick(self, ctx, arg1, arg2=None):
        await ctx.message.delete()
        if self.currentDraft is None:
            await ctx.send(dicts.NO_DRAFT, delete_after=DELAY)
        else:
            if (ctx.author.name == self.currentDraft.team_first.captain and self.currentDraft.turn() == 1) or (
                    ctx.author.name == self.currentDraft.team_second.captain and self.currentDraft.turn() == 0):
                kind = "map" if self.currentDraft.stage_num <= 4 else "hero"
                picks = isin(kind, arg1, arg2)
                if not picks:
                    await ctx.send(dicts.NO_MATCH.format(kind), delete_after=DELAY)
                # lock in pick
                else:
                    # check for banned picks
                    if any(pick in (self.currentDraft.team_first.map_bans
                                    + self.currentDraft.team_second.map_bans
                                    + self.currentDraft.team_first.hero_bans
                                    + self.currentDraft.team_second.hero_bans) for pick in picks):
                        await ctx.send(dicts.ILLEGAL_PICK.format(kind), delete_after=DELAY)
                    elif picks in (self.currentDraft.team_first.hero_picks
                                   + self.currentDraft.team_second.hero_picks):
                        await ctx.send(dicts.REDUNDANT_PICK.format(kind), delete_after=DELAY)
                    else:
                        self.currentDraft.lock(picks)
                        await self.status_verbose(ctx)
        await self.update_embed()

    @draft.command()
    async def help(self, ctx):
        embed = discord.Embed.from_dict(dicts.help_embed)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DraftCog(bot))
