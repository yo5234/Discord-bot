from discord.ext import commands
from datetime import datetime, timezone
from config.firebase import db

class MemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db.collection("joinDates").document(str(member.id)).set({
            "joinedAt": datetime.now(timezone.utc).isoformat(),
            "guildId": str(member.guild.id)
        })
        print(f"📥 {member} joined. Join date saved in Firestore.")

async def setup(bot):
    await bot.add_cog(MemberJoin(bot))
