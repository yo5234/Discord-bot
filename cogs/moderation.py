import discord
from discord.ext import commands
import config
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(eval(config.FIREBASE_CREDENTIALS))
    firebase_admin.initialize_app(cred)
db = firestore.client()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Track when users join and save to Firestore
    @commands.Cog.listener()
    async def on_member_join(self, member):
        join_time = datetime.now(timezone.utc)
        db.collection("join_dates").document(str(member.id)).set({"join_time": join_time.isoformat()})
        print(f"📥 {member} joined. Stored join time.")

    # ✅ Auto-ban users who leave before 30 days
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = self.bot.get_guild(config.GUILD_ID)
        if not guild or not guild.me.guild_permissions.ban_members:
            print("⚠️ Missing 'Ban Members' permission.")
            return

        doc = db.collection("join_dates").document(str(member.id)).get()
        if not doc.exists:
            print(f"⚠️ No join record for {member}. Skipping.")
            return

        join_time = datetime.fromisoformat(doc.to_dict()["join_time"])
        days_in_server = (datetime.now(timezone.utc) - join_time).days

        if days_in_server < 30:
            try:
                await guild.ban(member, reason="Left before 30 days")
                print(f"🚨 {member} was banned.")

                # ✅ DM the user
                try:
                    embed_dm = discord.Embed(title="🚨 You Have Been Banned", color=discord.Color.red())
                    embed_dm.add_field(name="Reason", value="Left before 30 days", inline=False)
                    embed_dm.add_field(name="Appeal", value=f"[Click here]({config.APPEAL_SERVER_INVITE})", inline=False)
                    await member.send(embed=embed_dm)
                except:
                    print(f"⚠️ Couldn't DM {member}.")
                
                # ✅ Log the ban
                log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
                if log_channel:
                    embed = discord.Embed(title="🚨 Auto-Ban Triggered", color=discord.Color.red())
                    embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                    embed.add_field(name="Reason", value="Left before 30 days", inline=False)
                    await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Ban failed: {e}")

    # ✅ Unban Command
    @commands.command()
    async def unban(self, ctx, user: discord.User):
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(title="❌ Permission Denied", description="You must be an **admin**.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        guild = self.bot.get_guild(config.GUILD_ID)
        if not guild:
            await ctx.send("⚠️ Guild not found.")
            return

        bans = await guild.bans()
        banned_users = [entry.user.id for entry in bans]

        if user.id not in banned_users:
            embed = discord.Embed(title="⚠️ User Not Banned", description=f"{user.mention} is **not banned**.", color=discord.Color.orange())
            await ctx.send(embed=embed)
            return

        await guild.unban(user)
        print(f"✅ {user} was unbanned.")

        # ✅ DM user
        try:
            embed_dm = discord.Embed(title="✅ You Have Been Unbanned", color=discord.Color.green())
            embed_dm.add_field(name="Server", value=guild.name, inline=False)
            await user.send(embed=embed_dm)
        except:
            print(f"⚠️ Couldn't DM {user}.")

        # ✅ Log unban
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
            embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
            await log_channel.send(embed=embed)

        embed_success = discord.Embed(title="✅ Unban Successful", description=f"{user.mention} has been unbanned.", color=discord.Color.green())
        await ctx.send(embed=embed_success)

# ✅ Add the cog
async def setup(bot):
    await bot.add_cog(Moderation(bot))
