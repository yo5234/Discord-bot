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
                dm_message = (
                    f"You have been banned from **{guild.name}** for leaving before 30 days.\n"
                    f"If you believe this was a mistake, you can appeal here: {APPEAL_SERVER_INVITE}"
                )
                await member.send(dm_message)
            except:
                pass  # Ignore errors if the user has DMs off

            # Log the ban in embed format
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="🚨 Auto-Ban Log",
                    description=f"{member.mention} was banned for leaving before 30 days.",
                    color=discord.Color.red(),
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                embed.add_field(name="User ID", value=member.id, inline=False)
                embed.add_field(name="Ban Reason", value="Left before 30 days", inline=False)
                await log_channel.send(embed=embed)

# ✅ Unban command (Admins Only) — Now with Embed Logs
@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, user: discord.User):
    guild = ctx.guild

    try:
        await guild.unban(user)
        await ctx.send(f"✅ {user.mention} has been unbanned.")

        # Log the unban in embed format
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="✅ Unban Log",
                description=f"{user.mention} has been unbanned.",
                color=discord.Color.green(),
            )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed.add_field(name="User ID", value=user.id, inline=False)
            embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
            await log_channel.send(embed=embed)
    
    except discord.NotFound:
        await ctx.send("❌ User is not banned or does not exist.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unban this user.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")

# Run the bot
bot.run(TOKEN)
