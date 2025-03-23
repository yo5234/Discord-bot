# Function to send DM and log errors in log channel
async def send_dm(user, embed):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    try:
        await user.send(embed=embed)
        print(f"📩 DM sent to {user}.")
    except discord.Forbidden:
        error_msg = f"⚠️ Cannot DM {user} (they have DMs closed or bot is blocked)."
        print(error_msg)
        if log_channel:
            embed_log = discord.Embed(title="⚠️ DM Failed", color=discord.Color.orange())
            embed_log.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
            embed_log.add_field(name="Reason", value="DMs closed or bot is blocked.", inline=False)
            await log_channel.send(embed=embed_log)
    except discord.HTTPException as e:
        error_msg = f"❌ DM failed for {user}: {e}"
        print(error_msg)
        if log_channel:
            embed_log = discord.Embed(title="❌ DM Error", color=discord.Color.red())
            embed_log.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
            embed_log.add_field(name="Error", value=str(e), inline=False)
            await log_channel.send(embed=embed_log)

# ✅ Auto-ban on leave
@bot.event
async def on_member_remove(member):
    await bot.wait_until_ready()
    guild = bot.get_guild(GUILD_ID)

    join_time = join_dates.get(member.id)  # Get stored join time
    if not join_time:
        print(f"⚠️ No stored join date for {member}. Skipping auto-ban.")
        return

    days_in_server = (datetime.now(timezone.utc) - join_time).days
    if days_in_server < 30:
        try:
            await guild.ban(member, reason="Left before 30 days")
            print(f"🚨 {member} was banned.")

            # DM banned user
            embed_dm = discord.Embed(title="🚨 You Have Been Banned", color=discord.Color.red())
            embed_dm.add_field(name="Reason", value="Left before 30 days", inline=False)
            embed_dm.add_field(name="Appeal", value=f"[Click here]({APPEAL_SERVER_INVITE})", inline=False)
            await send_dm(member, embed_dm)

            # Log the ban
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(title="🚨 Auto-Ban Triggered", color=discord.Color.red())
                embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
                embed.add_field(name="Reason", value="Left before 30 days", inline=False)
                await log_channel.send(embed=embed)
        except Exception as e:
            print(f"❌ Ban failed for {member}: {e}")

# ✅ Unban command
@bot.command()
async def unban(ctx, user: discord.User):
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(title="❌ Permission Denied", description="You must be an **admin** to use this command.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild = bot.get_guild(GUILD_ID)
    try:
        await guild.fetch_ban(user)
    except discord.NotFound:
        embed = discord.Embed(title="⚠️ User Not Banned", description=f"{user.mention} is **not banned**.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    await guild.unban(user)
    print(f"✅ {user} was unbanned.")

    # DM user
    embed_dm = discord.Embed(title="✅ You Have Been Unbanned", color=discord.Color.green())
    embed_dm.add_field(name="Server", value=guild.name, inline=False)
    await send_dm(user, embed_dm)

    # Log unban
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Unbanned By", value=ctx.author.mention, inline=False)
        await log_channel.send(embed=embed)

    embed_success = discord.Embed(title="✅ Unban Successful", description=f"{user.mention} has been unbanned.", color=discord.Color.green())
    await ctx.send(embed=embed_success)
