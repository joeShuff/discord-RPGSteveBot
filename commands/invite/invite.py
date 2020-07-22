import discord


async def invite_link(message, bot):
    link = "https://discord.com/oauth2/authorize?client_id={client}&scope=bot&permissions=268892224".replace("{client}", str(bot.user.id))

    embed = discord.Embed(title="Invite Link for " + str(bot.user.name), description="Oooo thanks for sharing me! I'll behave I promise... :eyes:")
    embed.add_field(name="Link", value="Invite me to another server [here](" + link + " 'Click me to invite!')")
    embed.set_thumbnail(url=bot.user.avatar_url)
    await message.channel.send(embed=embed)
