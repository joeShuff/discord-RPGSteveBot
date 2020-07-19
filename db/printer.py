from db.db_controller import *

import discord
import datetime

##TODO: IMPROVE THIS MESSAGE
async def no_character_found(channel):
    await channel.send("Can't find a character for you in this guild.")


##TODO: IMPROVE THIS MESSAGE
async def already_has_character_message(channel, character):
    await channel.send("It seems you already have a character in this guild. *" + str(character.character_name) + "*")


async def print_character_created_at(channel, created_at):
    char = get_character_created_at(created_at, str(channel.guild.id))
    await print_character(channel, char)


async def print_character_for_user(channel, user):
    char = get_character_for_owner(user, str(channel.guild.id))

    if char is not None:
        await print_character(channel, char)
    else:
        await no_character_found(channel)


async def print_character(channel, character, in_detail=False):
    main_embed = discord.Embed(
        color=0xff0000,
        title=character.character_name + " (" + character.character_slug + ")",
        timestamp=datetime.datetime.now()
    )

    if len(character.character_image) > 0:
        main_embed.set_image(character.character_image)

    main_stats_1 = [
        "**Strength**: " + str(character.strength) + " (*" + str(character.get_modifier(character.strength)) + "*)",
        "**Power**: " + str(character.power) + " (*" + str(character.get_modifier(character.power)) + "*)",
        "**Dexterity**: " + str(character.dexterity) + " (*" + str(character.get_modifier(character.dexterity)) + "*)",
        "**Intelligence**: " + str(character.intelligence) + " (*" + str(character.get_modifier(character.intelligence)) + "*)"
    ]

    main_stats_2 = [
        "**Education**: " + str(character.education) + " (*" + str(character.get_modifier(character.education)) + "*)",
        "**Size**: " + str(character.size) + " (*" + str(character.get_modifier(character.size)) + "*)",
        "**Constitution**: " + str(character.constitution) + " (*" + str(character.get_modifier(character.constitution)) + "*)",
        "**Appearance**: " + str(character.appearance) + " (*" + str(character.get_modifier(character.appearance)) + "*)"
    ]

    main_embed.add_field(name="Main Statistics", value="\n".join(main_stats_1), inline=True)
    main_embed.add_field(name="-----", value="\n".join(main_stats_2), inline=True)

    await channel.send(embed=main_embed)
