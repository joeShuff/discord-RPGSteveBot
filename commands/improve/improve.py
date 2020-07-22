from db.db_controller import *
import discord
from random import randrange


async def improvement_error_message(channel, message):
    await channel.send(message)


def improve_by(current_level):
    dice_result = 0
    dice_type = ""

    if current_level >= 85:
        dice_type = "d1"
        dice_result = 1
    elif current_level >= 70:
        dice_type = "d2"
        dice_result = randrange(1, 2)
    elif current_level >= 60:
        dice_type = "d3"
        dice_result = randrange(1, 3)
    elif current_level >= 50:
        dice_type = "d4"
        dice_result = randrange(1, 4)
    elif current_level >= 30:
        dice_type = "d5"
        dice_result = randrange(1, 5)
    else:
        dice_type = "d6"
        dice_result = randrange(1, 6)

    return dice_type, dice_result


async def check_improvements_from_reaction(reaction, reacting_user, message):
    check_mark = "✅"
    cross = '🚫'

    if not is_game_active_for_guild(str(message.guild.id)):
        return

    improvement_request = get_improvement_request_from_message(message.id)

    if improvement_request is None:
        return

    has_gm = next((x for x in reacting_user.roles if x.name == "GameMaster"), None) is not None

    if not has_gm:
        return

    character_requested = get_character_for_id(improvement_request.character_id)

    if reaction.name == cross:
        remove_character_improvement_requests(character_requested.id)
        request_message = await message.channel.fetch_message(improvement_request.improvement_message)

        denied_embed = discord.Embed(title="~~" + character_requested.character_name + " requested improvement~~",
                                       description="Improvement request was denied",
                                       color=0xff0000)

        await request_message.edit(embed=denied_embed)
        return

    if reaction.name != check_mark:
        return

    character = get_character_for_id(improvement_request.character_id)

    remove_character_improvement_requests(character_requested.id)
    await do_improvements(message.channel, character)


async def request_my_improvements(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not is_game_active_for_guild(guild):
        await improvement_error_message(message.channel, "The game in this guild isn't active right now.")
        return

    if has_gm:
        await improvement_error_message(message.channel, "You are a GM, you don't have a character to improve.")
        return

    my_character = get_character_for_owner(sender, guild)

    if my_character is None:
        await improvement_error_message(message.channel, "Cannot find a character for you in this guild.")
        return

    if character_has_improvement_request(my_character.id):
        await improvement_error_message(message.channel, "You already have an active improvement request in this guild.")
        return

    skills = [x for x in get_skills_for_character(my_character.id) if x.passed_prev == 1]

    if len(skills) == 0:
        await improvement_error_message(message.channel, "You haven't passed any skills therefore have nothing to improve! Sorry!")
        return

    approval_embed = discord.Embed(title=my_character.character_name + " requested improvement",
                                   description="GameMaster needs to approve this by reacting with :white_check_mark:\n"
                                               "Reject the request by reacting with :no_entry_sign:",
                                   color=0xffff00)

    approval = await message.channel.send(embed=approval_embed)

    set_improvement_requested(my_character.id, approval.id)

    await approval.add_reaction("✅")
    await approval.add_reaction('🚫')


async def do_improvements(channel, character_for):
    skills = [x for x in get_skills_for_character(character_for.id) if x.passed_prev == 1]

    embed = discord.Embed(title="Improvement Checks for " + str(character_for.character_name), color=0xff00ff)

    for skill in skills:
        improvement_message = "Current Level: " + str(skill.pass_level) + "\n"

        improvement_check = randrange(1, 100)
        improvement_message += "Check to Improve: `d100 = " + str(improvement_check) + "`\n"

        if improvement_check < skill.pass_level:
            improvement_message += "Failed to improve"
            set_skill(character_for.id, skill.skill_name, skill.pass_level, reset_pass=True)
        else:
            improvement_dice, improvement_result = improve_by(skill.pass_level)
            improvement_message += "Improve by: `" + improvement_dice + " = " + str(improvement_result) + "`\n"

            set_skill(character_for.id, skill.skill_name, skill.pass_level + improvement_result, reset_pass=True)
            improvement_message += "New Level: " + str((skill.pass_level + improvement_result))

        embed.add_field(name=skill.skill_name + " Improvement", value=improvement_message)

    await channel.send(embed=embed)