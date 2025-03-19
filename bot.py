import discord
import os
from discord.ext import commands
from datetime import datetime, timezone

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
APPEAL_SERVER_INVITE = os.getenv("APPEAL_SERVER_INVITE")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

join_times = {}  # Store user join times

# ✅ Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")

# ✅ Track when users join
@bot.event
async def on_member_join(member):
    join_times[member.id] = member.joined_at

# ✅ Auto-ban users who leave before 30 days
@bot.event
async def on_member_remove(member):
    await bot.wait_until_ready()  # Ensure bot is fully initialized

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("⚠️ Guild not found.")
        return

    if not guild.me.guild_permissions.ban_members:
        print("⚠️ Missing 'ban_members' permission.")
        return

    if member.id not in join_times:
        print(f"⚠️ {member} not found in join_times.")
        return

    time_joined = join_times[member.id]
    days_in_server = (datetime.now(timezone.utc) - time_joined).days

    if days_in_server < 30:
        await guild.ban(member, reason="Left before 30 days")

        # Send DM
        try:
            embed_dm = discord.Embed(title="🚨 You Have Been Banned", color=discord.Color.red())
            embed_dm.add_field(name="Reason", value="Left before 30 days", inline=False)
            embed_dm.add_field(name="Appeal", value=f"[Click here]({APPEAL_SERVER_INVITE})", inline=False)
            await member.send(embed=embed_dm)
        except:
            pass  # Ignore DM errors

        # Log the ban
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🚨 Auto-Ban Triggered", color=discord.Color.red())
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Reason", value="Left before 30 days", inline=False)
            await log_channel.send(embed=embed)
        else:
            print("⚠️ Log channel not found.")

# ✅ Unban Command (Admins Only)
@bot.command()
async def unban(ctx, user: discord.User):
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(title="❌ Permission Denied", description="You must be an **admin** to use this command.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        await ctx.send("⚠️ Guild not found.")
        return

    try:
        await guild.fetch_ban(user)
    except discord.NotFound:
        embed = discord.Embed(title="⚠️ User Not Banned", description=f"{user.mention} is **not banned**.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    await guild.unban(user)

    # DM user
    try:
        embed_dm = discord.Embed(title="✅ You Have Been Unbanned", color=discord.Color.green())
        embed_dm.add_field(name="Server", value=guild.name, inline=False)
        await user.send(embed=embed_dm)
    except:
        pass

    # Log unban
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
        await log_channel.send(embed=embed)

    embed_success = discord.Embed(title="✅ Unban Successful", description=f"{user.mention} has been unbanned.", color=discord.Color.green())
    await ctx.send(embed=embed_success)

# ✅ Error Handling
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

    if log_channel:
        embed_log = discord.Embed(title="⚠️ Command Error", color=discord.Color.orange())
        embed_log.add_field(name="Error", value=str(error), inline=False)
        embed_log.add_field(name="Command", value=ctx.message.content, inline=False)
        embed_log.add_field(name="User", value=ctx.author.mention, inline=False)
        await log_channel.send(embed=embed_log)

# Run the bot
bot.run(TOKEN)
