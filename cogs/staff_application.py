import discord
from discord.ext import commands
import os

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
OWNER_ID = 984152481225404467  # Your User ID
BLOCKED_ROLE_ID = 1354032792408948779  # Role that cannot apply

class StaffApplication(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="app")
    async def app_command(self, ctx):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("❌ You do not have permission to use this command.")

        embed = discord.Embed(
            title="📋 Click below to apply for staff!",
            color=discord.Color.blue()
        )

        view = discord.ui.View()
        view.add_item(ApplyButton())

        await ctx.send(embed=embed, view=view)

class ApplyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Apply", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        if BLOCKED_ROLE_ID in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("❌ You are not allowed to apply.", ephemeral=True)

        modal = StaffApplicationModal()
        await interaction.response.send_modal(modal)

class StaffApplicationModal(discord.ui.Modal, title="Staff Application"):
    why_pick = discord.ui.TextInput(
        label="Why should we pick you?",
        style=discord.TextStyle.paragraph,
        required=True
    )
    why_want = discord.ui.TextInput(
        label="Why do you want to be staff?",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = interaction.client.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📋 New Staff Application", color=discord.Color.green())
            embed.add_field(name="Applicant", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
            embed.add_field(name="Why should we pick you?", value=self.why_pick.value, inline=False)
            embed.add_field(name="Why do you want to be staff?", value=self.why_want.value, inline=False)
            await log_channel.send(embed=embed)

        await interaction.response.send_message("✅ Your application has been submitted!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(StaffApplication(bot))
