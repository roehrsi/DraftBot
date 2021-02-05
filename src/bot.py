import os

import discord
import json
import logging

from discord.ext import commands

logging.basicConfig(level=logging.INFO)
description = "This is a simple Bot to simulate drafting."
intents = discord.Intents.default()

with open("config.json", "r") as file:
    config = json.load(file)
    bot = commands.Bot(command_prefix=config["command_prefix"], description=config["description"], intents=intents)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

with open("token.json", "r") as token:
    jfile = json.load(token)
    bot.run(jfile["token"])
