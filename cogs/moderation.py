import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user_id: int):
        guild = ctx.guild
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)

        try:
            user = await self.bot.fetch_user(user_id)
            ban_entry = await guild.fetch_ban(user)  # Check if user is banned

            if not ban_entry:
                embed = discord.Embed(title="⚠️ User Not Banned", description=f"{user.mention} is not banned.", color=discord.Color.orange())
                await ctx.send(embed=embed)
                return

            await guild.unban(user)
            embed_success = discord.Embed(title="✅ Unban Successful", description=f"{user.mention} has been unbanned.", color=discord.Color.green())
            await ctx.send(embed=embed_success)

            # DM the user
            try:
                embed_dm = discord.Embed(title="✅ You Have Been Unbanned", color=discord.Color.green())
                embed_dm.add_field(name="Server", value=guild.name, inline=False)
                await user.send(embed=embed_dm)
            except:
                print(f"⚠️ Couldn't DM {user}.")
            
            # Log the unban
            if log_channel:
                embed_log = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
                embed_log.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
                embed_log.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
                await log_channel.send(embed=embed_log)

        except discord.NotFound:
            embed = discord.Embed(title="⚠️ User Not Found", description="Invalid user ID. Make sure the user was banned.", color=discord.Color.red())
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"❌ Error in unban: {e}")
            embed = discord.Embed(title="⚠️ Error", description=f"An error occurred: `{e}`", color=discord.Color.red())
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
