import discord
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")  # Get token from Railway environment variables
GUILD_ID = int(os.getenv("GUILD_ID"))  # Your main server ID
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Log channel ID
APPEAL_SERVER_INVITE = os.getenv("APPEAL_SERVER_INVITE")  # Appeal server invite link

intents = discord.Intents.all()

# ✅ Set bot with fixed prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

join_times = {}

# ✅ Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now online!")

# ✅ Auto-ban users who leave before 30 days
@bot.event
async def on_member_remove(member):
    if member.id in join_times:
        time_joined = join_times[member.id]
        time_now = asyncio.get_event_loop().time()
        days_in_server = (time_now - time_joined) / 86400  # Convert seconds to days
        
        if days_in_server < 30:
            guild = bot.get_guild(GUILD_ID)
            await guild.ban(member, reason="Left before 30 days")

            # Send DM to banned user
            try:
                dm_message = f"You have been banned from {guild.name} for leaving before 30 days.\n"
                dm_message += f"If you believe this was a mistake, you can appeal here: {APPEAL_SERVER_INVITE}"
                await member.send(dm_message)
            except:
                pass  # Ignore errors if the user has DMs off

            # Log the ban
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"🚨 {member.mention} was banned for leaving before 30 days.")

# ✅ Unban command (Admins Only, Supports Mentions)
@bot.command()
@commands.has_permissions(administrator=True)  # ✅ Only admins can use it
async def unban(ctx, user: discord.User):  # Accepts a mention or user ID
    guild = ctx.guild  # Get the guild (server)
    
    try:
        await guild.unban(user)  # Unban the user
        await ctx.send(f"✅ {user.mention} has been unbanned.")

        # ✅ DM the user (optional)
        try:
            await user.send(f"✅ You have been unbanned from {guild.name}. You may rejoin now.")
        except:
            pass  # Ignore errors if DMs are off

        # ✅ Log the unban
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"✅ {user.mention} has been unbanned by {ctx.author.mention}.")

    except discord.NotFound:
        await ctx.send("❌ This user is not banned or doesn't exist.")
    except discord.Forbidden:
        await ctx.send("❌ I do not have permission to unban members.")
    except discord.HTTPException as e:
        await ctx.send(f"⚠️ Discord API Error: {e}")
    except Exception as e:
        await ctx.send(f"⚠️ Unexpected Error: {e}")

# ✅ Run the bot
bot.run(TOKEN)
