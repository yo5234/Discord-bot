import discord from discord.ext import commands from discord.ui import Button, View

class AutoGiveawayPayout(commands.Cog): def init(self, bot): self.bot = bot

@commands.Cog.listener()
async def on_giveaway_end(self, giveaway):
    payout_channel_id = 1351971819682271332
    payout_channel = self.bot.get_channel(payout_channel_id)
    
    if payout_channel:
        winners = giveaway['winners']
        prize = giveaway['prize']
        divided_prize = prize / len(winners) if winners else prize
        
        winners_mention = ', '.join([f"<@{winner}>" for winner in winners])
        embed = discord.Embed(
            title="Giveaway Ended!",
            description=f"Prize: {prize} (Each winner gets {divided_prize})\nWinners: {winners_mention}",
            color=discord.Color.green()
        )
        
        button = Button(label="Queue this?", style=discord.ButtonStyle.primary)
        
        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Queued successfully!", ephemeral=True)
        
        button.callback = button_callback
        
        view = View()
        view.add_item(button)
        
        await payout_channel.send(embed=embed, view=view)

@commands.Cog.listener()
async def on_message(self, message):
    if message.author.id == 957635842631950379 and message.channel.id == 1351971819682271332:
        await message.delete()
        # Fetch latest giveaway results and resend the updated message
        # (Assume we have a method to get latest results)
        latest_giveaway = self.get_latest_giveaway()
        await self.on_giveaway_end(latest_giveaway)

async def setup(bot): await bot.add_cog(AutoGiveawayPayout(bot))

