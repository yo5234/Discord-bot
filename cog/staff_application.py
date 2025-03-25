import discord
from discord.ext import commands
import os

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
OWNER_ID = 984152481225404467  # Your Discord user ID

class StaffApplicationModal(discord.ui.Modal, title="Staff Application"):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.TextInput(label="Why should we pick you for staff?", style=discord.TextStyle.paragraph, required=True))
        self.add_item(discord.ui.TextInput(label="Why do you want to be staff?", style=discord.TextStyle.paragraph, required=True))

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = interaction.client.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📥 New Staff Application", color=discord.Color.blue())
            embed.add_field(name="Applicant", value=interaction.user.mention, inline=False)
            embed.add_field(name="Why should we pick you?", value=self.children[0].value, inline=False)
            embed.add_field(name="Why do you want to be staff?", value=self.children[1].value, inline=False)
            await log_channel.send(embed=embed)
        
        await interaction.response.send_message("✅ Your application has been submitted!", ephemeral=True)

class StaffApplication(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="app")
    async def apply(self, ctx):
        """Start the staff application process. Only the owner can use this."""
        if ctx.author.id != OWNER_ID:
            await ctx.send("❌ You do not have permission to use this command.", ephemeral=True)
            return
        await ctx.send("📋 Click below to apply for staff!", view=ApplyButton())

class ApplyButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Apply", style=discord.ButtonStyle.primary, custom_id="apply_staff"))

    @discord.ui.button(label="Apply", style=discord.ButtonStyle.primary)
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffApplicationModal())

async def setup(bot):
    await bot.add_cog(StaffApplication(bot))
