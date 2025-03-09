import discord
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
APPEAL_SERVER_INVITE = os.getenv("APPEAL_SERVER_INVITE")
MUTE_ROLE_ID = 1346086817572585482  # Muted role ID

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

join_times = {}

# ✅ Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now online!")
    for guild in bot.guilds:
        print(f"Connected to: {guild.name} (ID: {guild.id})")

# ✅ Help Command (Lists all commands)
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Command List", description="Here are all available commands:", color=discord.Color.gold())

    commands_list = {
        "**Moderation**": [
            "`!ban @user [reason]` - Ban a user",
            "`!kick @user [reason]` - Kick a user",
            "`!mute @user [reason]` - Mute a user",
            "`!unmute @user` - Unmute a user",
            "`!timeout @user duration [reason]` - Timeout a user"
        ],
        "**Utility**": [
            "`!ping` - Check bot latency",
            "`!userinfo [@user]` - Get user info",
            "`!serverinfo` - Get server info",
            "`!avatar [@user]` - Get user avatar"
        ],
        "**Roles**": [
            "`!role add @user RoleName` - Add a role",
            "`!role remove @user RoleName` - Remove a role"
        ]
    }

    for category, cmds in commands_list.items():
        embed.add_field(name=category, value="\n".join(cmds), inline=False)

    await ctx.send(embed=embed)

# ✅ Track when users join
@bot.event
async def on_member_join(member):
    join_times[member.id] = member.joined_at.timestamp()
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)

# ✅ Auto-ban users who leave before 30 days
@bot.event
async def on_member_remove(member):
    if member.id in join_times:
        time_joined = join_times[member.id]
        time_now = asyncio.get_event_loop().time()
        days_in_server = (time_now - time_joined) / 86400  

        if days_in_server < 30:
            guild = bot.get_guild(GUILD_ID)
            await guild.ban(member, reason="Left before 30 days")

            try:
                dm_message = f"You have been banned from {guild.name} for leaving before 30 days.\n"
                dm_message += f"If you believe this was a mistake, you can appeal here: {APPEAL_SERVER_INVITE}"
                await member.send(dm_message)
            except:
                pass  

            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"🚨 {member.mention} was banned for leaving before 30 days.")

# ✅ Unban command (Admins Only)
@bot.command()
async def unban(ctx, user_id: int):
    admin_users = ["secret_was_here", "deiman9000"]
    if str(ctx.author) not in admin_users:
        await ctx.send("❌ You are not allowed to use this command.")
        return
    
    guild = bot.get_guild(GUILD_ID)
    user = await bot.fetch_user(user_id)
    await guild.unban(user)
    
    try:
        await user.send(f"✅ You have been unbanned from {guild.name}. You may rejoin now.")
    except:
        pass  

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"✅ {user.mention} has been unbanned by {ctx.author.mention}.")

    await ctx.send(f"✅ {user.mention} has been unbanned.")

# ✅ Moderation Commands
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"✅ {member.mention} has been banned. Reason: {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} has been kicked. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if role and role not in member.roles:
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} has been muted. Reason: {reason}")
    else:
        await ctx.send("❌ User is already muted or mute role not found.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if role and role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"✅ {member.mention} has been unmuted.")
    else:
        await ctx.send("❌ User is not muted or mute role not found.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: int, *, reason="No reason provided"):
    time = duration * 60  
    await member.timeout_for(duration=time, reason=reason)
    await ctx.send(f"✅ {member.mention} has been timed out for {duration} minutes. Reason: {reason}")

# ✅ Utility Commands
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info - {member.name}", color=discord.Color.blue())
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M"), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.green())
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

# ✅ Role Management Command (Add & Remove Role)
@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, action: str, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send("❌ Role not found.")
        return

    if action.lower() == "add":
        await member.add_roles(role)
        await ctx.send(f"✅ Added role **{role.name}** to {member.mention}.")
    elif action.lower() == "remove":
        await member.remove_roles(role)
        await ctx.send(f"✅ Removed role **{role.name}** from {member.mention}.")
    else:
        await ctx.send("❌ Invalid action! Use `!role add @user RoleName` or `!role remove @user RoleName`.")

# Run the bot
bot.run(TOKEN)
