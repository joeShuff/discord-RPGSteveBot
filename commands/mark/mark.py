from db.db_controller import *
import discord


async def mark_error_message(channel, message):
    embed = discord.Embed(title="Mark Command Error",
                          color=0xff0000,
                          description=message)

    await channel.send(embed=embed)


async def mark_confirmation_message(channel, message):
    embed = discord.Embed(title="Mark Command Success",
                          color=0x00ff00,
                          description= message)

    await channel.send(embed=embed)


async def mark_skill_for_character(message, checked=True):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    guild = str(message.guild.id)

    is_game_active = is_game_active_for_guild(str(message.guild.id))

    if not is_game_active:
        await mark_error_message(message.channel, "The game in this guild isn't active right now.")
        return

    if has_gm:
        if len(parameters) < 2:
            await mark_error_message(message.channel, "Unknown syntax. Please follow `?mark <character_slug> <skillname>`")
            return
        else:
            character = get_character_for_slug(parameters[0], guild)

            skill = [x for x in get_skills_for_character(character.id) if x.skill_name.replace(" ", "").lower() == parameters[1].lower()]

            if len(skill) == 0:
                await mark_error_message(message.channel, "Cannot find a skill for `" + str(parameters[1]) + "`")
                return

            if character is None:
                await mark_error_message(message.channel, "Can't find a character with slug `" + parameters[0] + "` in this guild.")
            else:
                if checked:
                    mark_skill_as_passed(character.id, skill[0].skill_name)
                    await mark_confirmation_message(message.channel, "Marked `" + str(skill[0].skill_name) + "` as passed for " + str(character.character_name))
                else:
                    mark_skill_as_not_passed(character.id, skill[0].skill_name)
                    await mark_confirmation_message(message.channel, "Marked `" + str(skill[0].skill_name) + "` as NOT passed for " + str(character.character_name))
    else:
        await mark_error_message(message.channel, "This is a GM only command")