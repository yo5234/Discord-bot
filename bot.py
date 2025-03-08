import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta
import os

# Setup bot with intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Connect to SQLite database
conn = sqlite3.connect("members.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS members (user_id INTEGER, join_date TEXT)")
conn.commit()

APPEAL_SERVER_LINK = "https://discord.gg/6Sk9gpbAv2"  # Replace with your actual appeal server link

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    # Assign "Member" role
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)

    # Save join date
    cursor.execute("INSERT OR REPLACE INTO members (user_id, join_date) VALUES (?, ?)", 
                   (member.id, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

@bot.event
async def on_member_remove(member):
    # Get join date
    cursor.execute("SELECT join_date FROM members WHERE user_id = ?", (member.id,))
    result = cursor.fetchone()

    if result:
        join_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        if datetime.utcnow() - join_date < timedelta(days=30):
            # Ban the user if they leave before 30 days
            guild = member.guild
            await guild.ban(member, reason="Left before 30 days. Appeal in our appeal server.")

            # Attempt to DM the banned user
            try:
                await member.send(f"You have been banned for leaving before 30 days.\n"
                                  f"If you wish to appeal, please join our appeal server: {APPEAL_SERVER_LINK}")
            except discord.Forbidden:
                print(f"Could not DM {member.name} about their ban.")

    # Remove user from database
    cursor.execute("DELETE FROM members WHERE user_id = ?", (member.id,))
    conn.commit()

# Start the bot using a hidden token
bot.run(os.getenv("DISCORD_BOT_TOKEN"))