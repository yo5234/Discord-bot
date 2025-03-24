import discord
import os
from discord.ext import commands

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Unban Command
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user_id: int):
        """Unbans a user by ID and sends confirmation."""
        guild = ctx.guild
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)

        try:
            user = await self.bot.fetch_user(user_id)
            # Check if the user is banned
            bans = await guild.bans()
            banned_users = [ban_entry.user.id for ban_entry in bans]

            if user.id not in banned_users:
                embed = discord.Embed(title="⚠️ User Not Banned", description=f"{user.mention} is **not banned**.", color=discord.Color.orange())
                await ctx.send(embed=embed)
                return

            await guild.unban(user)
            embed_success = discord.Embed(title="✅ Unban Successful", description=f"{user.mention} has been **unbanned**.", color=discord.Color.green())
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
            embed_error = discord.Embed(title="❌ Error", description="User **not found**. Make sure the ID is correct.", color=discord.Color.red())
            await ctx.send(embed=embed_error)

        except discord.Forbidden:
            embed_error = discord.Embed(title="❌ Error", description="I **don't have permission** to unban users.", color=discord.Color.red())
            await ctx.send(embed=embed_error)

        except Exception as e:
            embed_error = discord.Embed(title="❌ Unexpected Error", description=f"An error occurred: `{e}`", color=discord.Color.red())
            await ctx.send(embed=embed_error)

    # ✅ Error Handling for Missing Permissions
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="❌ Permission Denied", description="You must be an **admin** to use this command.", color=discord.Color.red())
            await ctx.send(embed=embed)

# ✅ Setup function to add the cog
async def setup(bot):
    await bot.add_cog(Moderation(bot))
