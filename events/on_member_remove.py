from discord.ext import commands
from datetime import datetime, timezone
from config.firebase import db
import discord
import os

GUILD_ID = int(os.getenv("GUILD_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
APPEAL_SERVER_INVITE = os.getenv("APPEAL_SERVER_INVITE")

class MemberLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = self.bot.get_guild(GUILD_ID)
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)

        doc = db.collection("joinDates").document(str(member.id)).get()

        if not doc.exists:
            warning_message = f"⚠️ No join date for {member}. Skipping auto-ban."
            print(warning_message)

            # Log missing join date in the server
            if log_channel:
                embed = discord.Embed(title="⚠️ Auto-Ban Skipped", color=discord.Color.orange())
                embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                embed.add_field(name="Reason", value="No join date found in Firestore", inline=False)
                await log_channel.send(embed=embed)
            return

        join_data = doc.to_dict()
        joined_at = datetime.fromisoformat(join_data["joinedAt"])
        days_in_server = (datetime.now(timezone.utc) - joined_at).days

        if days_in_server < 30 and guild and guild.me.guild_permissions.ban_members:
            try:
                await guild.ban(member, reason="Left before 30 days")
                print(f"🚨 {member} was banned.")

                # DM user
                try:
                    embed_dm = discord.Embed(title="🚨 You Have Been Banned", color=discord.Color.red())
                    embed_dm.add_field(name="Reason", value="Left before 30 days", inline=False)
                    embed_dm.add_field(name="Appeal", value=f"[Click here]({APPEAL_SERVER_INVITE})", inline=False)
                    await member.send(embed=embed_dm)
                except:
                    print(f"⚠️ Couldn't DM {member}.")

                # Log the ban in the server
                if log_channel:
                    embed = discord.Embed(title="🚨 Auto-Ban Triggered", color=discord.Color.red())
                    embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                    embed.add_field(name="Reason", value="Left before 30 days", inline=False)
                    await log_channel.send(embed=embed)

            except Exception as e:
                error_message = f"❌ Ban failed for {member}: {e}"
                print(error_message)

                if log_channel:
                    embed = discord.Embed(title="❌ Auto-Ban Failed", color=discord.Color.red())
                    embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                    embed.add_field(name="Error", value=str(e), inline=False)
                    await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MemberLeave(bot))
