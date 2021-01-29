import discord
from discord.ext import commands
from dataclasses import dataclass
from random import randint
import json

description = ""

client = discord.Client()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', description=description, intents=intents)


@dataclass
class Team:
    captain = ""
    map_bans = {}
    map_pick = {}
    hero_bans = {}
    hero_picks = {}


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.group()
async def draft(ctx, message):
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "Welcome to the draft, {0}! If you want to draft a map, type ``!draft map´´ to start the coin flip and draft a map".format(
                ctx.author))
        await ctx.send("Otherwise use ``!draft quick [map]´´ to skip map draft and pick a map directly, then do the coin flip.")


@draft.command()
async def map(ctx):
    coin = randint(0, 1)
    await ctx.send("")


@draft.command()
async def quick(ctx, name=""):
    return

with open("token.json", "r") as token:
    json_file = json.load(token)
    client.run(json_file["token"])
