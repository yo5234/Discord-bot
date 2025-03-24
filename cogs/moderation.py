import discord
import os
import firebase_admin
from firebase_admin import firestore, credentials
from discord.ext import commands
from datetime import datetime, timezone

# Initialize Firebase
cred = credentials.Certificate(eval(os.getenv("FIREBASE_CREDENTIALS")))
firebase_admin.initialize_app(cred)
db = firestore.client()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Auto-track join dates
    @commands.Cog.listener()
    async def on_member_join(self, member):
        join_time = datetime.now(timezone.utc)
        db.collection("join_dates").document(str(member.id)).set({"join_date": join_time.isoformat()})
        print(f"📥 {member} joined. Stored join time.")

    # ✅ Auto-ban users who leave before 30 days
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = self.bot.get_guild(int(os.getenv("GUILD_ID")))
        log_channel = self.bot.get_channel(int(os.getenv("LOG_CHANNEL_ID")))

        if not guild or not guild.me.guild_permissions.ban_members:
            print("⚠️ Missing 'Ban Members' permission or guild not found.")
            return

        # Retrieve join date from Firebase
        doc_ref = db.collection("join_dates").document(str(member.id)).get()
        if not doc_ref.exists:
            print(f"⚠️ No join date stored for {member}. Skipping auto-ban.")
            return

        join_time = datetime.fromisoformat(doc_ref.to_dict()["join_date"])
        days_in_server = (datetime.now(timezone.utc) - join_time).days
        print(f"ℹ️ {member} was in the server for {days_in_server} days.")

        if days_in_server < 30:
            try:
                await guild.ban(member, reason="Left before 30 days")
                print(f"🚨 {member} was banned.")

                # DM the banned user
                try:
                    embed_dm = discord.Embed(title="🚨 You Have Been Banned", color=discord.Color.red())
                    embed_dm.add_field(name="Reason", value="Left before 30 days", inline=False)
                    embed_dm.add_field(name="Appeal", value=f"[Click here]({os.getenv('APPEAL_SERVER_INVITE')})", inline=False)
                    await member.send(embed=embed_dm)
                except:
                    print(f"⚠️ Couldn't DM {member}.")

                # Log the ban
                if log_channel:
                    embed = discord.Embed(title="🚨 Auto-Ban Triggered", color=discord.Color.red())
                    embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                    embed.add_field(name="Reason", value="Left before 30 days", inline=False)
                    await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Ban failed for {member}: {e}")

    # ✅ Unban command with error handling
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user_id: int):
        guild = ctx.guild
        log_channel = self.bot.get_channel(int(os.getenv("LOG_CHANNEL_ID")))

        try:
            bans = await guild.bans()
            banned_user = discord.utils.get(bans, user__id=user_id)

            if banned_user is None:
                embed = discord.Embed(title="⚠️ User Not Found", description="This user is not banned.", color=discord.Color.orange())
                await ctx.send(embed=embed)
                return

            await guild.unban(banned_user.user)
            embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
            embed.add_field(name="User", value=f"{banned_user.user.mention} ({banned_user.user.id})", inline=False)
            embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)

            # DM the unbanned user
            try:
                dm_embed = discord.Embed(title="✅ You Have Been Unbanned", color=discord.Color.green())
                dm_embed.add_field(name="Server", value=guild.name, inline=False)
                await banned_user.user.send(embed=dm_embed)
            except:
                print(f"⚠️ Couldn't DM {banned_user.user}")

            # Log the unban
            if log_channel:
                await log_channel.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(title="❌ Permission Denied", description="I don't have permission to unban users.", color=discord.Color.red()))
        except discord.HTTPException as e:
            await ctx.send(embed=discord.Embed(title="❌ Error", description=f"An error occurred: `{e}`", color=discord.Color.red()))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
