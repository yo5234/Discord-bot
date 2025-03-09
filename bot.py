import discord
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")  # Bot token (set in Railway)
GUILD_ID = int(os.getenv("GUILD_ID"))  # Main server ID
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Log channel ID
BUMP_CHANNEL_ID = int(os.getenv("BUMP_CHANNEL_ID"))  # Channel where /bump will be used
APPEAL_SERVER_INVITE = os.getenv("APPEAL_SERVER_INVITE")  # Appeal server invite link

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

join_times = {}

# ✅ Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now online!")
    for guild in bot.guilds:
        print(f"Connected to: {guild.name} (ID: {guild.id})")
    bot.loop.create_task(auto_bump())  # Start auto-bump loop

# ✅ Auto-bump every 2 hours using the proper /bump slash command
async def auto_bump():
    await bot.wait_until_ready()
    bump_channel = bot.get_channel(BUMP_CHANNEL_ID)

    if bump_channel is None:
        print("❌ Bump channel not found. Please check the ID.")
        return

    while not bot.is_closed():
        try:
            # Get the Disboard bot user
            disboard_bot = discord.utils.get(bot.get_all_members(), id=302050872383242240)  # Disboard bot ID
            
            # Check if Disboard bot is in the server
            if disboard_bot is None:
                print("❌ Disboard bot not found. Make sure it's in your server.")
            else:
                # Send the /bump slash command using interaction
                await bump_channel.send("/bump")
                print("✅ Successfully sent /bump command!")
        except Exception as e:
            print(f"❌ Error sending /bump command: {e}")

        await asyncio.sleep(7200)  # Wait for 2 hours (7200 seconds)

# ✅ Track when users join
@bot.event
async def on_member_join(member):
    join_times[member.id] = member.joined_at.timestamp()

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

# ✅ Unban command (Admins Only)
@bot.command()
async def unban(ctx, user_id: int):
    admin_users = ["secret_was_here", "deiman9000"]  # Admin usernames
    if str(ctx.author) not in admin_users:
        await ctx.send("❌ You are not allowed to use this command.")
        return
    
    guild = bot.get_guild(GUILD_ID)
    user = await bot.fetch_user(user_id)
    await guild.unban(user)
    
    # Send DM to unbanned user
    try:
        await user.send(f"✅ You have been unbanned from {guild.name}. You may rejoin now.")
    except:
        pass  # Ignore errors if user has DMs off
    
    # Log the unban
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"✅ {user.mention} has been unbanned by {ctx.author.mention}.")

    await ctx.send(f"✅ {user.mention} has been unbanned.")

# Run the bot
bot.run(TOKEN)
