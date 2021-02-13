import os

import discord
import json
import logging

from discord.ext import commands

token = os.environ.get("DTOKEN", "NO TOKEN")

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
        print(f"cogs.{name}", "loaded")

bot.run(token)
