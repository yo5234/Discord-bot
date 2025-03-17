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
                embed_dm = discord.Embed(title="🚨 You Have Been Banned", color=discord.Color.red())
                embed_dm.add_field(name="Reason", value="Left before 30 days", inline=False)
                embed_dm.add_field(name="Appeal", value=f"[Click here]({APPEAL_SERVER_INVITE})", inline=False)
                await member.send(embed=embed_dm)
            except:
                pass  # Ignore errors if DMs are off

            # Log the ban with an embed
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(title="🚨 Auto-Ban Triggered", color=discord.Color.red())
                embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                embed.add_field(name="Reason", value="Left before 30 days", inline=False)
                await log_channel.send(embed=embed)

# ✅ Unban Command (Admins Only, Improved Check)
@bot.command()
async def unban(ctx, user: discord.User):
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(title="❌ Permission Denied", description="You must be an **admin** to use this command.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    guild = bot.get_guild(GUILD_ID)

    # Check if user is actually banned
    try:
        ban_entry = await guild.fetch_ban(user)  # Fetch ban details
    except discord.NotFound:
        embed = discord.Embed(title="⚠️ User Not Banned", description=f"{user.mention} is **not banned**.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    # Unban the user
    await guild.unban(user)

    # Send DM to unbanned user
    try:
        embed_dm = discord.Embed(title="✅ You Have Been Unbanned", color=discord.Color.green())
        embed_dm.add_field(name="Server", value=guild.name, inline=False)
        await user.send(embed=embed_dm)
    except:
        pass  # Ignore errors if user has DMs off

    # Log the unban with an embed
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
        await log_channel.send(embed=embed)

    embed_success = discord.Embed(title="✅ Unban Successful", description=f"{user.mention} has been unbanned.", color=discord.Color.green())
    await ctx.send(embed=embed_success)

# ✅ Error Handling with Embedded Messages
@bot.event
async def on_command_error(ctx, error):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="❌ Permission Denied", description="You don’t have permission to use this command.", color=discord.Color.red())
    elif isinstance(error, commands.UserNotFound):
        embed = discord.Embed(title="⚠️ User Not Found", description="Please mention a valid user.", color=discord.Color.orange())
    else:
        embed = discord.Embed(title="⚠️ Unexpected Error", description=f"An error occurred: `{error}`", color=discord.Color.orange())

    await ctx.send(embed=embed)

    # Log the error
    if log_channel:
        embed_log = discord.Embed(title="⚠️ Command Error", color=discord.Color.orange())
        embed_log.add_field(name="Error", value=str(error), inline=False)
        embed_log.add_field(name="Command", value=ctx.message.content, inline=False)
        embed_log.add_field(name="User", value=ctx.author.mention, inline=False)
        await log_channel.send(embed=embed_log)

# Run the bot
bot.run(TOKEN)
