from db.db_controller import *


async def today_error_message(channel, message):
    await channel.send(message)


async def do_today_command(message):
    is_game_active = is_game_active_for_guild(str(message.guild.id))

    guild = str(message.guild.id)

    embed = discord.Embed(title="Stability Today",
                          color=0xffbf00)

    if not is_game_active:
        embed.add_field(name="Game Not Active", value="The game in this guild isn't active right now.")

    characters = get_characters_in_guild(guild, incl_inactive=False)

    today_stats = []

    for character in characters:
        if character.start_of_day_stability is None or character.stability_curr is None:
            continue

        damage_today = abs(character.start_of_day_stability - character.stability_curr)
        percentage_stab_lost_today = (float(damage_today) / float(character.start_of_day_stability) * 100.0)

        today_stats.append("`" + character.character_name + "` has suffered " + str(damage_today) + " damage today (" + ("%.2f" % percentage_stab_lost_today) + "%)")

    embed.add_field(name="Todays Stability Damage", value="\n".join(today_stats), inline=False)

    await message.channel.send(embed=embed)