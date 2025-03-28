import discord from discord.ext import commands import re

PAYOUT_CHANNEL_ID = 1351971819682271332  # Payouts channel ID ELEMENT_BOT_ID = 957635842631950379  # Element bot ID

class AutoGiveawayPayout(commands.Cog): def init(self, bot): self.bot = bot self.payout_messages = {}  # Stores message IDs for rerolls

@commands.Cog.listener()
async def on_message(self, message: discord.Message):
    if message.author.id == ELEMENT_BOT_ID and "winners:" in message.content.lower():
        winner_match = re.findall(r"(@\S+)", message.content)
        prize_match = re.search(r"\b(\d{1,3}(?:,\d{3})*)\b", message.content)
        
        if winner_match and prize_match:
            winners = winner_match
            total_prize = int(prize_match.group(1).replace(",", ""))
            prize_per_winner = total_prize // len(winners) if winners else total_prize
            
            queue_embed = discord.Embed(title="Queue Winners?", color=discord.Color.blurple())
            queue_embed.add_field(name="Winners", value=", ".join(winners), inline=False)
            queue_embed.add_field(name="Total Prize", value=f"⦿ {total_prize}", inline=False)
            queue_embed.add_field(name="Prize per Winner", value=f"⦿ {prize_per_winner}", inline=False)
            
            view = discord.ui.View()
            button = discord.ui.Button(label="Queue This?", style=discord.ButtonStyle.primary)
            button.callback = lambda i: self.queue_payout(i, winners, prize_per_winner)
            view.add_item(button)
            
            await message.channel.send(embed=queue_embed, view=view)

async def queue_payout(self, interaction: discord.Interaction, winners: list, prize: int):
    payout_channel = self.bot.get_channel(PAYOUT_CHANNEL_ID)
    if not payout_channel:
        return
    
    embed = discord.Embed(title="Payout Queued", color=discord.Color.gold())
    embed.add_field(name="Winners", value=", ".join(winners), inline=False)
    embed.add_field(name="Prize per Winner", value=f"⦿ {prize}", inline=False)
    embed.set_footer(text=f"Queued by {interaction.user.display_name}")
    
    message = await payout_channel.send(embed=embed)
    self.payout_messages[", ".join(winners)] = message.id

@commands.Cog.listener()
async def on_message_edit(self, before: discord.Message, after: discord.Message):
    if before.author.id == ELEMENT_BOT_ID and "rerolled winners:" in after.content.lower():
        winner_match = re.findall(r"(@\S+)", after.content)
        prize_match = re.search(r"\b(\d{1,3}(?:,\d{3})*)\b", after.content)
        
        if winner_match and prize_match:
            winners = winner_match
            total_prize = int(prize_match.group(1).replace(",", ""))
            prize_per_winner = total_prize // len(winners) if winners else total_prize
            
            payout_channel = self.bot.get_channel(PAYOUT_CHANNEL_ID)
            if not payout_channel:
                return
            
            if before.content in self.payout_messages:
                try:
                    msg_id = self.payout_messages.pop(before.content)
                    msg_to_delete = await payout_channel.fetch_message(msg_id)
                    await msg_to_delete.delete()
                except discord.NotFound:
                    pass
            
            await self.queue_payout(after, winners, prize_per_winner)

async def setup(bot): await bot.add_cog(AutoGiveawayPayout(bot))

