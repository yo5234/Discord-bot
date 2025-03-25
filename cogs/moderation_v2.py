import discord
from discord.ext import commands
import re

MUTE_ROLE_ID = 1346086817572585482  # Mute role ID directly set in code

class ModerationV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Assigns the mute role to a user"""
        mute_role = ctx.guild.get_role(MUTE_ROLE_ID)
        if not mute_role:
            return await ctx.send("⚠️ Mute role not found!")

        try:
            await member.add_roles(mute_role, reason=reason)
            embed = discord.Embed(title="🔇 User Muted", color=discord.Color.orange())
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("⚠️ I couldn't mute this user!")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Removes the mute role from a user"""
        mute_role = ctx.guild.get_role(MUTE_ROLE_ID)
        if not mute_role:
            return await ctx.send("⚠️ Mute role not found!")

        try:
            await member.remove_roles(mute_role)
            embed = discord.Embed(title="🔊 User Unmuted", color=discord.Color.green())
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("⚠️ I couldn't unmute this user!")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kicks a user from the server"""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(title="👢 User Kicked", color=discord.Color.red())
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("⚠️ I couldn't kick this user!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Bans a user from the server"""
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="🚫 User Banned", color=discord.Color.dark_red())
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("⚠️ I couldn't ban this user!")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """Locks the current channel"""
        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
            embed = discord.Embed(title="🔒 Channel Locked", color=discord.Color.dark_gray())
            embed.add_field(name="Channel", value=ctx.channel.mention, inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("⚠️ I couldn't lock this channel!")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        """Unlocks the current channel"""
        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
            embed = discord.Embed(title="🔓 Channel Unlocked", color=discord.Color.green())
            embed.add_field(name="Channel", value=ctx.channel.mention, inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("⚠️ I couldn't unlock this channel!")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason="No reason provided"):
        """Timeouts a user for a specified duration using formats like 60m, 2h, 3d, 1w, 1y"""
        
        if member is None:
            return await ctx.send("⚠️ You must mention a user to timeout!")
        
        if duration is None:
            return await ctx.send("⚠️ You must provide a duration (e.g., `60m`, `2h`, `3d`, `1w`, `1y`)!")

        # Convert duration to seconds
        duration_mapping = {
            "m": 60,         # minutes
            "h": 3600,       # hours
            "d": 86400,      # days
            "w": 604800,     # weeks
            "y": 31536000    # years
        }
        
        match = re.match(r"^(\d+)([mhdwy])$", duration)
        if not match:
            return await ctx.send("⚠️ Invalid duration format! Use `60m`, `2h`, `3d`, `1w`, `1y`.")

        amount, unit = match.groups()
        seconds = int(amount) * duration_mapping[unit]

        try:
            await member.timeout(discord.utils.utcnow() + discord.timedelta(seconds=seconds), reason=reason)
            
            embed = discord.Embed(title="⏳ User Timed Out", color=discord.Color.orange())
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Duration", value=f"{amount} {unit}", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"⚠️ I couldn't timeout this user! Error: `{e}`")

async def setup(bot):
    await bot.add_cog(ModerationV2(bot))
