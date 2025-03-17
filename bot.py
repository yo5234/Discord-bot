import discord
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")  # Get token from Railway environment variables
GUILD_ID = int(os.getenv("GUILD_ID"))  # Your main server ID
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Log channel ID
APPEAL_SERVER_INVITE = os.getenv("APPEAL_SERVER_INVITE")  # Appeal server invite link

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

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

            # Log the ban with an embed
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(title="🚨 Auto-Ban Triggered", color=discord.Color.red())
                embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                embed.add_field(name="Reason", value="Left before 30 days", inline=False)
                await log_channel.send(embed=embed)

# ✅ Unban Command (Admins Only, Checks if User is Banned)
@bot.command()
async def unban(ctx, user: discord.User):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You must be an admin to use this command.")
        return
    
    guild = bot.get_guild(GUILD_ID)
    
    # Get ban list
    bans = await guild.bans()
    banned_users = [ban_entry.user.id for ban_entry in bans]
    
    if user.id not in banned_users:
        await ctx.send(f"⚠️ {user.mention} is **not banned**.")
        return
    
    # Unban the user
    await guild.unban(user)

    # Send DM to unbanned user
    try:
        await user.send(f"✅ You have been unbanned from {guild.name}. You may rejoin now.")
    except:
        pass  # Ignore errors if user has DMs off

    # Log the unban with an embed
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
        await log_channel.send(embed=embed)

    await ctx.send(f"✅ {user.mention} has been unbanned.")

# Run the bot
bot.run(TOKEN)
