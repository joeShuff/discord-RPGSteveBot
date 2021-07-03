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


async def print_character(context, character, in_detail=False):
    main_embed = discord.Embed(
        color=0xff0000,
        title=character.character_name + " (" + character.character_slug + ")"
    )

    owner = character.owner_id

    if owner != "NPC":
        owner = "<@!" + str(owner) + ">"

    if len(character.character_image) > 0:
        main_embed.set_image(url=character.character_image)

    main_stats_1 = [
        "**Strength**: " + str(character.strength) + " (*" + str(character.get_modifier(character.strength)) + "*)",
        "**Education**: " + str(character.education) + " (*" + str(character.get_modifier(character.education)) + "*)",
        "**Power**: " + str(character.power) + " (*" + str(character.get_modifier(character.power)) + "*)",
        "**Size**: " + str(character.size) + " (*" + str(character.get_modifier(character.size)) + "*)",
        "**Dexterity**: " + str(character.dexterity) + " (*" + str(character.get_modifier(character.dexterity)) + "*)",
        "**Constitution**: " + str(character.constitution) + " (*" + str(character.get_modifier(character.constitution)) + "*)",
        "**Intelligence**: " + str(character.intelligence) + " (*" + str(character.get_modifier(character.intelligence)) + "*)",
        "**Appearance**: " + str(character.appearance) + " (*" + str(character.get_modifier(character.appearance)) + "*)"
    ]

    all_skills = get_skills_for_character(character.id)

    def to_readable(n):
        return str(n.skill_name) + " -> `" + str(n.pass_level) + "`"

    all_skills = map(to_readable, all_skills)

    health_text = str(character.hitpoints_curr) + "/" + str(character.hitpoints_max)
    stability_text = str(character.stability_curr) + "/" + str(character.stability_max)

    if character.insane == 1:
        stability_text += " **INSANE**"
    elif character.unstable == 1:
        stability_text += " **UNSTABLE**"

    speed_text = str(character.speed)
    xp_text = "Level " + str(character.level) + " (" + str(character.xp) + " XP)"

    main_embed.add_field(name="Owner", value=owner, inline=True)
    main_embed.add_field(name="Health", value=health_text, inline=True)
    main_embed.add_field(name="Stability", value=stability_text, inline=True)
    main_embed.add_field(name="Speed", value=speed_text, inline=True)
    main_embed.add_field(name="Level & XP", value=xp_text, inline=True)

    main_embed.add_field(name="Base Skills", value="\n".join(main_stats_1), inline=False)

    if in_detail:
        main_embed.add_field(name="Skills", value=" | ".join(all_skills))

    await context.send(embed=main_embed)
