import discord from discord.ext import commands import re

class AutoGiveawayPayout(commands.Cog): def init(self, bot): self.bot = bot

@commands.Cog.listener()
async def on_message(self, message):
    # Check if the message is from the Element bot and contains a giveaway result
    if message.author.id == 957635842631950379 and "GIVEAWAY ENDED" in message.content:
        winners = re.findall(r'@\S+', message.content)
        prize_match = re.search(r'(\d+[mkb])', message.content, re.IGNORECASE)
        
        if winners and prize_match:
            prize = prize_match.group(1)
            total_winners = len(winners)
            divided_prize = f"{int(prize[:-1]) // total_winners}{prize[-1]}" if total_winners > 0 else prize
            
            embed = discord.Embed(title="Payout Queued", color=discord.Color.gold())
            embed.add_field(name="Winners", value=', '.join(winners), inline=False)
            embed.add_field(name="Prize", value=f"Each gets: {divided_prize}", inline=False)
            
            view = discord.ui.View()
            button = discord.ui.Button(label="Queue", style=discord.ButtonStyle.green, custom_id="queue_giveaway")
            view.add_item(button)
            
            await message.channel.send(embed=embed, view=view)

@commands.Cog.listener()
async def on_interaction(self, interaction: discord.Interaction):
    if interaction.data and interaction.data.get("custom_id") == "queue_giveaway":
        await interaction.response.send_message("Giveaway queued successfully!", ephemeral=True)

async def setup(bot): await bot.add_cog(AutoGiveawayPayout(bot))

