import json
from random import randint

import discord
from discord.ext import commands, tasks

from src import dicts
from src.data import *
from src.util import isin

DELAY = 10
DELETE_DRAFT_EMOJI = "❌"


class DraftCog(commands.Cog, name="DraftCog"):
    def __init__(self, bot):
        self.bot = bot
        # there my only be one active draft per member!
        self.pending_drafts = {
            # member.id : Draft
        }

    with open("config.json", "r") as file:
        jfile = json.load(file)
        VERBOSE = jfile["verbose"]

    """async def status_verbose(self, ctx):
        if self.VERBOSE:
            draft = self.get_user_draft(ctx.author)
            if draft:
                if draft.stage_num == draft.MAP_PICK:
                    await ctx.send(
                        f"{draft.team_second.captain} can now ``!pick`` a map from the remaining pool.",
                        delete_after=DELAY)
                if draft.stage_num == draft.MAP_PICK + 1:
                    await ctx.send(
                        f"{draft.team_second.captain} picked **{draft.team_second.map_pick}**!\n"
                        f"Please start banning two heroes each by writing ``!ban [hero]``. {draft.team_first.captain} goes first!",
                        delete_after=DELAY)
                if draft.stage() == FIRST_PICK:
                    await ctx.send(f"{draft.team_first.captain.name} has the first pick!", delete_after=DELAY)
                if draft.stage() == (SECOND_HERO_BANS or FIRST_HERO_BANS):
                    await ctx.send(f"{draft.team_second.captain.name} bans another hero next!", delete_after=DELAY)
                if draft.stage() == (FIRST_HERO_PICKS or SECOND_HERO_PICKS):
                    await ctx.send(f"{draft.team_second.captain.name} continues picking!", delete_after=DELAY)"""

    def get_user_draft(self, member: discord.Member) -> Draft:
        return self.pending_drafts.get(member.id)

    @staticmethod
    def print_embed(draft: Draft):
        embed = discord.Embed(title="Draft:", color=0xff8040)
        embed.add_field(name=draft.team_first.captain.display_name, value=repr(draft.team_first),
                        inline=True)
        embed.add_field(name=draft.team_second.captain.display_name, value=repr(draft.team_second),
                        inline=True)
        embed.add_field(name="Status:", value=draft.status(), inline=False)
        return embed

    async def update_embed(self, member: discord.Member):
        draft: Draft = self.pending_drafts.get(member.id)
        message: discord.Message = draft.draft_message
        await message.edit(embed=self.print_embed(draft))
        # remove captains from pending drafts. clear reactions
        if draft.stage() == FIN:
            await message.clear_reactions()
            self.pending_drafts.pop(draft.team_first.captain.id)
            if draft.team_first.captain.id != draft.team_second.captain.id:
                self.pending_drafts.pop(draft.team_second.captain.id)

    @staticmethod
    def greeting(ctx):
        return dicts.GREETING.format(ctx.author.mention)

    @commands.group()
    async def draft(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send(self.greeting(ctx), delete_after=20)

    @draft.command(aliases=["t"])
    async def tournament(self, ctx, member: discord.Member):
        draft = Draft()
        if randint(0, 1):
            draft.team_first = Team(captain=ctx.author)
            draft.team_second = Team(captain=member)
        else:
            draft.team_first = Team(captain=member)
            draft.team_second = Team(captain=ctx.author)
        message = await ctx.send(embed=self.print_embed(draft))
        await message.add_reaction(DELETE_DRAFT_EMOJI)
        draft.draft_message = message
        self.pending_drafts.update({ctx.author.id: draft, member.id: draft})

    @draft.command(aliases=["q"])
    async def quick(self, ctx, arg, member: discord.Member):
        draft = Draft()
        kind = "map"
        match = isin(kind, arg)
        if match:
            draft.team_second = Team(captain=ctx.author, map_bans=["-", "-"], map_pick=match[0])
            draft.team_first = Team(captain=member, map_bans=["-", "-"])
            # set the stage to 5 (hero bans)
            draft.stage_num = 5
            message = await ctx.send(embed=self.print_embed(draft))
            draft.draft_message = message
            await message.add_reaction(DELETE_DRAFT_EMOJI)
            self.pending_drafts.update({ctx.author.id: draft, member.id: draft})
            """await ctx.send(
                f"{draft.team_second.captain.display_name} picked **{draft.team_second.map_pick}**!\n "
                f"Please start banning two heroes each by writing ``!ban [hero]``. "
                f"{draft.team_first.captain.display_name} goes first!",
                delete_after=DELAY)"""
        else:
            await ctx.send(dicts.NO_MATCH.format(kind), delete_after=DELAY)

    @commands.command()
    async def ban(self, ctx, arg):
        await ctx.message.delete()
        draft = self.get_user_draft(ctx.author)
        if not draft:
            await ctx.send(dicts.NO_DRAFT, delete_after=DELAY)
        else:
            if draft.phase() == BAN \
                    and ((ctx.author.id == draft.team_first.captain.id and draft.turn() == 0) or (
                    ctx.author.id == draft.team_second.captain.id and draft.turn() == 1)):
                kind = "map" if draft.stage_num <= 4 else "hero"
                # notice bans are always single arguments.
                bans = isin(kind, arg)
                if not bans:
                    await ctx.send(dicts.NO_MATCH.format(kind), delete_after=DELAY)
                # lock in the ban
                else:
                    # check bans for duplicates
                    if any(bans in (draft.team_first.map_bans
                                    + draft.team_second.map_bans
                                    + draft.team_first.hero_bans
                                    + draft.team_second.hero_bans) for bans in bans):
                        await ctx.send(dicts.ILLEGAL_PICK.format(kind), delete_after=DELAY)
                    elif any(bans in (draft.team_first.hero_picks
                                      + draft.team_second.hero_picks) for bans in bans):
                        await ctx.send(dicts.REDUNDANT_PICK.format(kind), delete_after=DELAY)
                    else:
                        draft.lock(bans)
                        # await self.status_verbose(ctx)
        await self.update_embed(ctx.author)

    @commands.command()
    async def pick(self, ctx, arg1, arg2=None):
        await ctx.message.delete()
        draft = self.get_user_draft(ctx.author)
        if not draft:
            await ctx.send(dicts.NO_DRAFT, delete_after=DELAY)
        else:
            if draft.phase() == PICK \
                    and ((ctx.author.id == draft.team_first.captain.id and draft.turn() == 0) or (
                    ctx.author.id == draft.team_second.captain.id and draft.turn() == 1)):
                kind = "map" if draft.stage_num <= 4 else "hero"
                picks = isin(kind, arg1, arg2)
                if not picks:
                    await ctx.send(dicts.NO_MATCH.format(kind), delete_after=DELAY)
                # lock in pick
                else:
                    # check for banned picks
                    if any(picks in (draft.team_first.map_bans
                                     + draft.team_second.map_bans
                                     + draft.team_first.hero_bans
                                     + draft.team_second.hero_bans) for picks in picks):
                        await ctx.send(dicts.ILLEGAL_PICK.format(kind), delete_after=DELAY)
                    elif any(picks in (draft.team_first.hero_picks
                                       + draft.team_second.hero_picks) for picks in picks):
                        await ctx.send(dicts.REDUNDANT_PICK.format(kind), delete_after=DELAY)
                    else:
                        print("turn: ", draft.turn(), draft.turn(draft.stage_num + 1))
                        if (picks == ["Cho", "Gall"]) and (draft.turn() != draft.turn(draft.stage_num + 1)):
                            await ctx.send("Must pick Cho'Gall during double pick phases :(", delete_after=DELAY)
                        else:
                            draft.lock(picks)
                            # await self.status_verbose(ctx)
        await self.update_embed(ctx.author)

    @draft.command()
    async def help(self, ctx):
        embed = discord.Embed.from_dict(dicts.help_embed)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DraftCog(bot))
