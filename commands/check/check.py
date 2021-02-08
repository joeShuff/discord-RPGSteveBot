from db.db_controller import *
from commands.set.set import base_stats
from random import randrange
import discord
import math

modifiers = {
    "DEX": "dexterity",
    "STR": "strength",
    "POW": "power",
    "EDU": "education",
    "SIZ": "size",
    "CON": "constitution",
    "APP": "appearance",
    "INT": "intelligence"
}

async def skill_check_error_message(channel, message):
    await channel.send(message)


async def skill_check_for_character(message, character, skill_search, adv=False, disadv=False):
    chosen_stat_name = ""
    chosen_stat_pass_value = 0
    chosen_modifier = "NON"

    checkable_skill = False

    is_game_active = is_game_active_for_guild(str(message.guild.id))

    skill_search = skill_search.lower().replace(" ", "")

    for key in base_stats.keys():
        if skill_search in base_stats[key]:
            chosen_stat_name = key
            chosen_stat_pass_value = character.get_stat(key.lower())
            break

    from db.db_controller import get_skills_for_character
    other_skills = get_skills_for_character(character.id)

    for skill in other_skills:
        if skill_search == skill.skill_name.lower().replace(" ", ""):
            chosen_stat_name = skill.skill_name
            chosen_modifier = skill.modifier
            chosen_stat_pass_value = get_skill(character.id, chosen_stat_name)
            checkable_skill = True
            break

    if chosen_stat_name == "":
        await skill_check_error_message(message.channel, "Cannot find a skill for `" + skill_search + "`")
        return

    roll_result = randrange(1, 100)
    other_roll = randrange(1, 100)

    modifier_amount = 0

    if chosen_modifier != "NON":
        if chosen_modifier in modifiers.keys():
            modifier_amount = character.get_modifier(character.get_stat(modifiers[chosen_modifier]))

    chosen_roll = roll_result

    roll_output_text = str(roll_result)

    if adv:
        if roll_result < other_roll:
            roll_output_text = str(roll_result) + " ~~" + str(other_roll) + "~~"
        else:
            roll_output_text = "~~" + str(roll_result) + "~~ " + str(other_roll)
            chosen_roll = other_roll
    elif disadv:
        if roll_result > other_roll:
            roll_output_text = str(roll_result) + " ~~" + str(other_roll) + "~~"
        else:
            roll_output_text = "~~" + str(roll_result) + "~~ " + str(other_roll)
            chosen_roll = other_roll

    roll_output_text = "`d100` = " + roll_output_text

    chosen_roll = min(100, max(chosen_roll + modifier_amount, 0))
    result_message = str(chosen_roll) + " = "

    if chosen_roll <= chosen_stat_pass_value and checkable_skill and is_game_active:
        mark_skill_as_passed(character.id, chosen_stat_name)

    if float(chosen_roll) <= chosen_stat_pass_value / 4.0:
        result_message += "ACE :white_check_mark:"
    elif chosen_roll <= chosen_stat_pass_value:
        result_message += "PASS :white_check_mark:"
    elif chosen_roll == 100:
        result_message += "oof, couldn't fail more"
    elif chosen_roll >= 98:
        result_message += "CRITICAL FAIL"
    else:
        result_message += "FAIL"

    if chosen_roll == 69:
        result_message += " *Nice*"

    embed = discord.Embed(title=character.character_name + "'s " + chosen_stat_name + " Check",
                          color=0x00ff00)

    if not is_game_active:
        embed.add_field(name="Offline Roll", value="This guilds game is offline so successful rolls aren't stored.", inline=False)

    dice_url = "https://raw.githubusercontent.com/joeShuff/discord-RPGSteveBot/master/art/dice/d{amount}.png"
    embed.set_thumbnail(url=dice_url.replace("{amount}", str(chosen_roll)))

    embed.add_field(name="Target", value=str(chosen_stat_pass_value), inline=True)
    embed.add_field(name="Rolled", value=str(roll_output_text), inline=True)

    if chosen_modifier != "NON":
        embed.add_field(name="Modifier", value=str(modifier_amount) + " (" + chosen_modifier + ")", inline=True)

    embed.add_field(name="Result", value=result_message, inline=False)
    embed.set_footer(text="rolled using SteveBot", icon_url="https://cdn.discordapp.com/avatars/731917492498333767/30d2df49893355093a5a1bfc52ca175e.webp?size=1024")

    await message.channel.send(embed=embed)


async def perform_skill_check(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if has_gm:
        if len(parameters) == 2 or len(parameters) == 3:
            char = get_character_for_slug(parameters[0], guild)

            adv = False
            disadv = False

            if len(parameters) == 3:
                adv = parameters[2].lower() == "a"
                disadv = parameters[2].lower() == "d"

            if char is not None:
                await skill_check_for_character(message, char, parameters[1], adv, disadv)
            else:
                await skill_check_error_message(message.channel, "Can't find a character with slug `" + parameters[0] + "` in this guild.")
        else:
            await skill_check_error_message(message.channel, "As the game master you have to use the syntax `?check <char slug> <skill name>`")
    else:
        if len(parameters) == 1 or len(parameters) == 2:
            my_char = get_character_for_owner(sender, guild)

            adv = False
            disadv = False

            if len(parameters) == 2:
                adv = parameters[1].lower() == "a"
                disadv = parameters[1].lower() == "d"

            if my_char is None:
                await skill_check_error_message(message.channel, "You don't have a character in this guild")
            else:
                await skill_check_for_character(message, my_char, parameters[0], adv, disadv)
        else:
            await skill_check_error_message(message.channel, "Unknown syntax. Please do `?help check` for more info.")

