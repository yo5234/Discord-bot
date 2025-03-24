from discord.ext import commands
import discord
import os

GUILD_ID = int(os.getenv("GUILD_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def unban(self, ctx, user: discord.User):
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(title="❌ Permission Denied", description="You must be an **admin** to use this command.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            await ctx.send("⚠️ Guild not found.")
            return

        try:
            await guild.unban(user)
            print(f"✅ {user} was unbanned.")

            # DM user
            try:
                embed_dm = discord.Embed(title="✅ You Have Been Unbanned", color=discord.Color.green())
                embed_dm.add_field(name="Server", value=guild.name, inline=False)
                await user.send(embed=embed_dm)
            except:
                print(f"⚠️ Couldn't DM {user}.")

            # Log unban
            log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
                embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
                embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
                await log_channel.send(embed=embed)

            embed_success = discord.Embed(title="✅ Unban Successful", description=f"{user.mention} has been unbanned.", color=discord.Color.green())
            await ctx.send(embed=embed_success)

        except Exception as e:
            print(f"❌ Unban failed: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
