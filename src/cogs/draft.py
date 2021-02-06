import json
from random import randint

import discord
from discord.ext import commands
from src.data import *
from src.util import isin


class DraftCog(commands.Cog, name="DraftCog"):
    def __init__(self, bot):
        self.bot = bot
        self.currentDraft = None

    class Warn:
        NO_DRAFT = "No draft is currently happening here... But you can change that!\n" \
                   "Please start a draft first, by typing ``!draft``.\n"
        NO_MAP = "I couldn't find a map with that name. :(\n" \
                 "Maybe try again with a different map."
        NO_HERO = "I couldn't find a hero with that name. :(\n" \
                  "Maybe try again with a different name."

    with open("config.json", "r") as file:
        jfile = json.load(file)
        VERBOSE = jfile["verbose"]

    @commands.group()
    async def draft(self, ctx):
        self.currentDraft = Draft()
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
            self.currentDraft.team_first = Team(captain=ctx.author.name)
            self.currentDraft.team_second = Team(captain="Opponent")
            s = f"{self.currentDraft.team_first.captain} won the coin toss! Your opponent can start banning a map now."
        else:
            self.currentDraft.team_first = Team(captain="Opponent")
            self.currentDraft.team_second = Team(captain=ctx.author.name)
            s = f"Opponent won the coin toss! {self.currentDraft.team_second.captain} starts banning a map."

        await ctx.send(s)

    @draft.command()
    async def quick(self, ctx, arg):
        if arg is not None:
            match = isin("maps", arg)
            if match:
                self.currentDraft.team_second = Team(captain=ctx.author.name, map_bans=["-", "-"], map_pick=match[0])
                self.currentDraft.team_first = Team(captain="Opponent", map_bans=["-", "-"])
                self.currentDraft.stage_num = 5
                s = "{0} picked **{1}**!\n".format(self.currentDraft.team_second.captain,
                                                   self.currentDraft.team_second.map_pick)
                s += "Please start banning two heroes each by writing ``!ban [hero]``. Opponent goes first!"
            else:
                s = self.Warn.NO_MAP
            await ctx.send(s)

    @commands.command()
    async def ban(self, ctx, arg):
        if self.currentDraft is None:
            s = self.Warn.NO_DRAFT
            return
        kind = "maps" if self.currentDraft.stage_num <= 4 else "heroes"
        bans = isin(kind, arg)
        if not bans:
            s = f"I could not find a {kind} with that name. :("
            await ctx.send(s)
            return
        self.currentDraft.lock(bans)
        if self.VERBOSE:
            if self.currentDraft.stage_num == 4:
                s = f"{self.currentDraft.team_second.captain} can now pick a map from the remaining pool."
                await ctx.send(s)
            if self.currentDraft.stage_num == 5:
                s = "{0} picked **{1}**!\n".format(self.currentDraft.team_second.captain,
                                                   self.currentDraft.team_second.map_pick)
                s += "Please start banning two heroes each by writing ``!ban [hero]``. Opponent goes first!"
                await ctx.send(s)
            if self.currentDraft.stage_num == 9:
                s = f"{self.currentDraft.team_first.captain} has the first pick!"
                await ctx.send(s)
            if self.currentDraft.stage_num == 14:
                s = f"{self.currentDraft.team_second.captain} bans another hero next!"
                await ctx.send(s)
            if self.currentDraft.stage_num == 16:
                s = f"{self.currentDraft.team_second.captain} continues picking!"
                await ctx.send(s)
        if self.currentDraft.stage_num == 21:
            await self.display(ctx)
            self.currentDraft = None

    @commands.command()
    async def pick(self, ctx, arg1, arg2=None):
        if self.currentDraft is None:
            s = "No draft is currently happening here... But you can change that!\n"
            s += "Please start a draft first, by typing ``!draft``.\n"
            await ctx.send(s)
            return
        kind = "maps" if self.currentDraft.stage_num <= 4 else "heroes"
        picks = isin(kind, arg1, arg2)
        if not picks:
            s = f"I could not find a {kind} with that name. :("
            await ctx.send(s)
            return
        self.currentDraft.lock(picks)
        if self.VERBOSE:
            if self.currentDraft.stage_num == 4:
                s = f"{self.currentDraft.team_second.captain} can now pick a map from the remaining pool."
                await ctx.send(s)
            if self.currentDraft.stage_num == 5:
                s = "Continue banning four heroes in turn"
                await ctx.send(s)
            if self.currentDraft.stage_num == 9:
                s = f"{self.currentDraft.team_first.captain} has the first pick!"
                await ctx.send(s)
            if self.currentDraft.stage_num == 14:
                s = f"{self.currentDraft.team_second.captain} bans another hero next!"
                await ctx.send(s)
            if self.currentDraft.stage_num == 16:
                s = f"{self.currentDraft.team_second.captain} continues picking!"
                await ctx.send(s)
        if self.currentDraft.stage_num == 21:
            await self.display(ctx)
            # self.currentDraft = None

    @commands.command()
    async def display(self, ctx):
        if self.currentDraft is None:
            s = self.Warn.NO_DRAFT
            await ctx.send(s)
            return
        await self.print_draft(ctx)

    @draft.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Hey there!",
                              description="This is DraftBot. He can help you draft the team of your dream in "
                                          "Heroes of the Storm! Take a minute to read the command doc below "
                                          "to get started.",
                              color=0xff8040)
        embed.set_author(name="DraftBot", url="https://github.com/roehrsi/DraftBot")
        embed.add_field(name="!draft",
                        value="To start a draft, the **!draft** command will begin a fresh draft for you. "
                              "Use either the **!draft tournament** command if you wannt to start with flipping a coin "
                              "for the first pick and drafting a map, or **!draft quick** if you want to pick a map "
                              "directly and move on to the hero draft.",
                        inline=False)
        embed.add_field(name="!ban",
                        value="The **!ban** command is you one stop shop for banning maps and heroes. "
                              "It takes one argument - the map or hero name - and adds that to the draft.",
                        inline=False)
        embed.add_field(name="!pick", value="The **!pick** command works just like **!ban** for map and hero picks."
                                            "For the double pick phases, the **!pick** command also takes two "
                                            "arguments.",
                        inline=False)
        embed.add_field(name="!display",
                        value="The **!display** command displays the current state of the draft. "
                              "After the draft completes, a summary will be shown containing all "
                              "the picked maps and heroes.",
                        inline=False)
        embed.add_field(name="!draft help", value="Use the **!draft help** command to display this information.",
                        inline=False)
        embed.add_field(name="!draft verbosity",
                        value="Use the **!draft verbosity [0/1]** command to adjust how talkative "
                              "DraftBot should be during the draft.",
                        inline=False)
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

    @draft.command()
    async def verbosity(self, ctx, arg):
        with open("config.json", "w") as file:
            jfile = json.load(file)
            if arg == 0 or 1:
                jfile["verbose"] = arg
                await ctx.send(f"Verbosity has been set to {'True' if arg == 1 else 'False'}")

    async def print_draft(self, ctx):
        if self.currentDraft is None:
            s = self.Warn.NO_DRAFT
            await ctx.send(s)
            return
        embed = discord.Embed(title="Finished Draft:", color=0xff8040)

        first_content = ("Map Bans: \n"
                         "```" + ", ".join(self.currentDraft.team_first.map_bans) + "```" +
                         "**Map Pick**: \n"
                         "```" + self.currentDraft.team_first.map_pick + "```" +
                         "**Hero Bans**: \n"
                         "```" + "\n".join(self.currentDraft.team_first.hero_bans) + "```" +
                         "**Hero Picks**: \n" +
                         "```" + "\n".join(self.currentDraft.team_first.hero_picks) + "```")

        second_content = ("Map Bans: \n"
                          "```" + ", ".join(self.currentDraft.team_second.map_bans) + "```" +
                          "**Map Pick**: \n"
                          "```" + self.currentDraft.team_second.map_pick + "```" +
                          "**Hero Bans**: \n"
                          "```" + "\n".join(self.currentDraft.team_second.hero_bans) + "```" +
                          "**Hero Picks**: \n" +
                          "```" + "\n".join(self.currentDraft.team_second.hero_picks) + "```")

        embed.add_field(name=self.currentDraft.team_first.captain, value=first_content, inline=True)
        embed.add_field(name=self.currentDraft.team_second.captain, value=second_content, inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DraftCog(bot))
