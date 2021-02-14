import json
from random import randint

import discord
from discord.ext import commands
from src.data import *
from src.util import isin

DELAY = 10

NO_DRAFT = "No draft is currently happening here... But you can change that!\n" \
           "Please start a draft first, by typing ``!draft``.\n"
NO_MATCH = "I couldn't find a {0} with that name. :(\n" \
           "Maybe try again with a more precise name."
GREETING = "Welcome to the draft, {0} \n " \
           "If you want to draft a map, type ``!draft tournament`` to start the coin flip and draft a map.\n " \
           "Otherwise use ``!draft quick [map]`` to skip map draft and pick a map directly, then do the coin flip.\n " \
           "If you want to restart the draft, simply call this base command again to reset all parameters."
REDUNDANT_PICK = "This {0} is already picked. Try something different."
ILLEGAL_PICK = "You cannot pick a banned {0}."


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
                    f"{self.currentDraft.team_second.captain} can now ```!pick``` a map from the remaining pool.",
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
        embed = discord.Embed(title="Draft:", color=0xff8040)
        embed.add_field(name=self.currentDraft.team_first.captain, value=repr(self.currentDraft.team_first),
                        inline=True)
        embed.add_field(name=self.currentDraft.team_second.captain, value=repr(self.currentDraft.team_second),
                        inline=True)
        return embed

    async def update_embed(self):
        if self.embed is not None:
            await self.embed.edit(embed=self.print_embed())

    @staticmethod
    def greeting(ctx):
        return GREETING.format(ctx.author.mention)

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
            s = f"{self.currentDraft.team_first.captain} won the coin toss! {self.currentDraft.team_second.captain} can start ```!ban```ning a map now."
        else:
            self.currentDraft.team_first = Team(captain=member.name)
            self.currentDraft.team_second = Team(captain=ctx.author.name)
            s = f"{self.currentDraft.team_first.captain} won the coin toss! {self.currentDraft.team_second.captain} starts ```!ban```ning a map."
        self.embed = await ctx.send(embed=self.print_embed())
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
            await ctx.send(
                f"{self.currentDraft.team_second.captain} picked **{self.currentDraft.team_second.map_pick}**!\n "
                f"Please start banning two heroes each by writing ``!ban [hero]``. {self.currentDraft.team_first.captain} goes first!",
                delete_after=DELAY)
        else:
            await ctx.send(NO_MATCH.format(kind), delete_after=DELAY)

    @commands.command()
    async def ban(self, ctx, arg):
        await ctx.message.delete()
        if self.currentDraft is None:
            await ctx.send(NO_DRAFT, delete_after=DELAY)
        else:
            if (ctx.author.name == self.currentDraft.team_first.captain and self.currentDraft.turn() == 1) or (
                    ctx.author.name == self.currentDraft.team_second.captain and self.currentDraft.turn() == 0):
                kind = "map" if self.currentDraft.stage_num <= 4 else "hero"
                bans = isin(kind, arg)
                if not bans:
                    await ctx.send(NO_MATCH.format(kind), delete_after=DELAY)
                # lock in the ban
                else:
                    # check bans for duplicates
                    if any(ban in (self.currentDraft.team_first.map_bans
                                   + self.currentDraft.team_second.map_bans
                                   + self.currentDraft.team_first.hero_bans
                                   + self.currentDraft.team_second.hero_bans) for ban in bans):
                        await ctx.send(REDUNDANT_PICK.format(kind), delete_after=DELAY)
                    else:
                        self.currentDraft.lock(bans)
                        await self.status_verbose(ctx)
        await self.update_embed()

    @commands.command()
    async def pick(self, ctx, arg1, arg2=None):
        await ctx.message.delete()
        if self.currentDraft is None:
            await ctx.send(NO_DRAFT, delete_after=DELAY)
        else:
            if (ctx.author.name == self.currentDraft.team_first.captain and self.currentDraft.turn() == 1) or (
                    ctx.author.name == self.currentDraft.team_second.captain and self.currentDraft.turn() == 0):
                kind = "map" if self.currentDraft.stage_num <= 4 else "hero"
                picks = isin(kind, arg1, arg2)
                if not picks:
                    await ctx.send(NO_MATCH.format(kind), delete_after=DELAY)
                # lock in pick
                else:
                    # check for banned picks
                    if any(pick in (self.currentDraft.team_first.map_bans
                                    + self.currentDraft.team_second.map_bans
                                    + self.currentDraft.team_first.hero_bans
                                    + self.currentDraft.team_second.hero_bans) for pick in picks):
                        await ctx.send(ILLEGAL_PICK.format(kind), delete_after=DELAY)
                    elif picks in (self.currentDraft.team_first.hero_picks
                                   + self.currentDraft.team_second.hero_picks):
                        await ctx.send(REDUNDANT_PICK.format(kind), delete_after=DELAY)
                    else:
                        self.currentDraft.lock(picks)
                        await self.status_verbose(ctx)
        await self.update_embed()

    @draft.command()
    async def display(self, ctx):
        if self.currentDraft is None:
            await ctx.send(NO_DRAFT, delete_after=DELAY)
        else:
            await ctx.send(embed=self.print_embed())

    @draft.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Hey there!",
                              description="*honk honk* This is DraftBot. He can help you draft the team of your dream in "
                                          "Heroes of the Storm! Take a minute to read the command doc below "
                                          "to get started.",
                              color=0xff8040)
        embed.set_author(name="DraftBot", url="https://github.com/roehrsi/DraftBot")
        embed.add_field(name="!draft",
                        value="To start a draft, the **!draft** command will begin a fresh draft for you. "
                              "Use either the **!draft tournament [@Opponent]** command if you want to start with "
                              "flipping a coin for the first pick and drafting a map, or **!draft quick [@Opponent]** "
                              "if you want to pick a map directly and move on to the hero draft. "
                              "Only you and your tagged opponent can influence the draft, "
                              "so you are safe from griefers and run-downers ;). "
                              "Nobody can stop you from tagging yourself though...",
                        inline=False)
        embed.add_field(name="!ban",
                        value="The **!ban** command is your one stop shop for banning maps and heroes. "
                              "It takes one argument - the map or hero name - and adds that to the draft."
                              "DraftBot can handle some spelling error and shorthands, "
                              "but try not to be too obscure with your inputs",
                        inline=False)
        embed.add_field(name="!pick", value="The **!pick** command works just like **!ban** for map and hero picks."
                                            "For the double pick phases, the **!pick** command also takes two "
                                            "arguments.",
                        inline=False)
        """embed.add_field(name="!display",
                        value="The **!display** command displays the current state of the draft. "
                              "After the draft completes, a summary will be shown containing all "
                              "the picked maps and heroes.",
                        inline=False)"""
        embed.add_field(name="!draft help", value="Use the **!draft help** command to display this information.",
                        inline=False)
        """embed.add_field(name="!draft verbosity",
                        value="Use the **!draft verbosity [0/1]** command to adjust how talkative "
                              "DraftBot should be during the draft.",
                        inline=False)"""
        embed.add_field(name="drafting order",
                        value="Order adheres to HotS tournament draft standard with **A** as coin toss winner: \n"
                              "Map Bans: **B A B A**\n"
                              "Map Pick: **B**\n"
                              "Hero Bans: **A B A B**\n"
                              "Hero Picks: **A BB AA**\n"
                              "Hero Bans: **B A**\n"
                              "Hero Picks: **BB AA B**",
                        inline=False)
        embed.set_footer(text="GL HF!")
        await ctx.send(embed=embed)

    # todo fix verbose set
    """
    @draft.command()
    async def verbosity(self, ctx, arg):
        with open("config.json", "w") as file:
            jfile = json.load(file)
            if arg == 0 or 1:
                jfile["verbose"] = arg
                await ctx.send(f"Verbosity has been set to {'True' if arg == 1 else 'False'}")
    """


def setup(bot):
    bot.add_cog(DraftCog(bot))
