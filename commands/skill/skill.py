from db.db_controller import *
import discord


async def skill_error_message(channel, message):
    embed = discord.Embed(title="Skill Command Error",
                          color=0xff0000,
                          description=message)

    await channel.send(embed=embed)


async def skill_confirmation_message(channel, message):
    embed = discord.Embed(title="Skill Command Success",
                          color=0x00ff00,
                          description= message)

    await channel.send(embed=embed)


async def create_new_skill(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    guild = str(message.guild.id)

    if has_gm:
        if len(parameters) < 4:
            await skill_error_message(message.channel, "Unknown syntax. Please follow `?skill create <slug> <skill> <value>")
            return
        else:
            characters = []

            if parameters[1] == "@everyone":
                characters = get_characters_in_guild(guild, False, True)
            else:
                characters.append(get_character_for_slug(parameters[1], guild))

            skill_name = parameters[2].title()
            skill_value = parameters[3]
            int_skill_value = 100

            try:
                int_skill_value = int(skill_value)
            except:
                await skill_error_message(message.channel, "Invalid skill value, please make sure you enter a number.")
                return

            if len(characters) == 0:
                await skill_error_message(message.channel, "Cannot find character with slug `" + str(parameters[1]) + "` in this guild!")
            else:
                for character in characters:
                    check_skill = get_skill(character.id, skill_name)

                    if check_skill is not None:
                        await skill_error_message(message.channel, "A skill titled " + str(skill_name) + " already exists for " + str(character.character_name))
                        return

                    if int_skill_value < 0 or int_skill_value > 70:
                        await skill_error_message(message.channel, "Please enter a value between 0 and 70")
                    else:
                        create_custom_skill(character.id, skill_name, int_skill_value)
                        await skill_confirmation_message(message.channel, "New skill, `" + str(skill_name) + "` has been created for `" + str(character.character_name) + "`.")
    else:
        await skill_error_message(message.channel, "This is a GM only command")