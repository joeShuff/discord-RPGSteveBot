from db.db_controller import *


async def set_day_error_message(channel, message):
    await channel.send(message)


async def do_day_reset(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None

    is_game_active = is_game_active_for_guild(str(message.guild.id))

    guild = str(message.guild.id)

    if not is_game_active:
        await set_day_error_message(message.channel, "The game in this guild isn't active right now.")
        return

    embed = discord.Embed(title="Good Mornin'",
                          color=0xffbf00)

    new_targets = []

    if has_gm:
        characters = get_characters_in_guild(guild, incl_inactive=False)

        insane_characters = []
        unstable_characters = []

        for character in characters:
            reset_day_stability(character)

            if character.unstable == 1:
                unstable_characters.append(character.character_name)

            if character.insane == 1:
                insane_characters.append(character.character_name)

            new_targets.append(str(character.character_name) + " starts today with `" + str(character.stability_curr) + "` stability.")

        embed.add_field(name="Starting Stability", value="\n".join(new_targets))

        if len(insane_characters) > 0:
            embed.add_field(name="Insane Characters", value="\n".join(insane_characters), inline=False)

        if len(unstable_characters) > 0:
            embed.add_field(name="Unstable Characters", value="\n".join(unstable_characters), inline=False)

        await message.channel.send(embed=embed)
    else:
        await set_day_error_message(message.channel, "You are not a GM in this guild!")
        return
