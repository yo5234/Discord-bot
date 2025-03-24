import discord
import os
import asyncio
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    await bot.load_extension("events.on_member_join")
    await bot.load_extension("events.on_member_remove")
    await bot.load_extension("cogs.moderation")

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    await load_cogs()

bot.run(TOKEN)
