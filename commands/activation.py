from db.db_controller import *


async def activation_error_message(channel, message):
    await channel.send(message)


async def activate_character(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not has_gm:
        await activation_error_message(message.channel, "This command is for Game Masters only!")
        return

    if len(parameters) == 0:
        await activation_error_message(message.channel, "Unknown syntax. Try `?help activate` for more info!")
        return

    char = get_character_for_slug(parameters[0], guild)

    if char is None:
        await activation_error_message(message.channel, "Cannot find a character with slug `" + str(parameters[0]) + "` in this guild!")
        return

    if is_character_active(char.id):
        await activation_error_message(message.channel, "Character *" + str(char.character_name) + "* is already active!")
        return

    set_character_activation(char.id, 1)

    await message.channel.send("Successfully Activated *" + str(char.character_name) + "*")


async def deactivate_character(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not has_gm:
        await activation_error_message(message.channel, "This command is for Game Masters only!")
        return

    if len(parameters) == 0:
        await activation_error_message(message.channel, "Unknown syntax. Try `?help activate` for more info!")
        return

    char = get_character_for_slug(parameters[0], guild)

    if char is None:
        await activation_error_message(message.channel,"Cannot find a character with slug `" + str(parameters[0]) + "` in this guild!")
        return

    if not is_character_active(char.id):
        await activation_error_message(message.channel, "Character *" + str(char.character_name) + "* is already inactive!")
        return

    set_character_activation(char.id, 0)

    await message.channel.send("Successfully Deactivated *" + str(char.character_name) + "*")