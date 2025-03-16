import discord
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")  # Get token from Railway environment variables
GUILD_ID = int(os.getenv("GUILD_ID"))  # Your main server ID
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Log channel ID
APPEAL_SERVER_INVITE = os.getenv("APPEAL_SERVER_INVITE")  # Appeal server invite link

intents = discord.Intents.all()

# ✅ Set Prefix to "!"
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

join_times = {}

# ✅ Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now online!")
    print("🔄 Syncing commands...")

    try:
        await bot.tree.sync()
        print("✅ Commands synced successfully!")
    except Exception as e:
        print(f"❌ Command sync failed: {e}")

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

# ✅ Test Command: Check Your Discord ID
@bot.command()
async def myid(ctx):
    await ctx.send(f"Your Discord ID is: `{ctx.author.id}`")

# ✅ Unban command (Admins Only - Restricted to Specific Users)
@bot.command()
async def unban(ctx, user_id: int):
    allowed_admins = [984152481225404467, 944332591404826645]  # Your Correct Discord User IDs

    print(f"🔍 Command used by: {ctx.author.id}")  # Debugging

    # Check if the command user is in the allowed list
    if ctx.author.id not in allowed_admins:
        await ctx.send(f"❌ You are not allowed to use this command. Your ID: `{ctx.author.id}`")
        return

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        await ctx.send("❌ Error: Bot is not in the correct server.")
        return

    try:
        print(f"Fetching ban list for {guild.name}...")  # Debugging
        banned_users = await guild.bans()
        user = discord.utils.get(banned_users, user__id=user_id)

        if user:
            await guild.unban(user.user)
            await ctx.send(f"✅ {user.user.mention} has been unbanned.")

            try:
                await user.user.send(f"✅ You have been unbanned from {guild.name}. You may rejoin now.")
            except:
                pass  # Ignore errors if DMs are off

            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"✅ {user.user.mention} has been unbanned by {ctx.author.mention}.")
        else:
            await ctx.send("❌ This user is not banned or does not exist in the ban list.")

    except discord.Forbidden:
        await ctx.send("❌ I do not have permission to unban members. Please check my role settings.")
    except discord.HTTPException as e:
        await ctx.send(f"⚠️ Discord API Error: {e}")
    except Exception as e:
        await ctx.send(f"⚠️ Unexpected Error: {e}")

# ✅ Error Handling - Tell Users If a Command Fails
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    else:
        raise error

# Run the bot
bot.run(TOKEN)
