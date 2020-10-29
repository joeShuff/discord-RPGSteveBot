from db.db_controller import *

from db.printer import *


async def me_error_message(channel, message):
    await channel.send(message)


async def me_command(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not has_gm:
        char = get_character_for_owner(sender, guild)

        if char is None:
            await me_error_message(message.channel, "Can't find a character for you in this guild!")
            return

        await print_character(message.channel, char, True)
    else:
        if len(parameters) == 0:
            await me_error_message(message.channel, "Please enter a slug to get character info for.")
            return

        char = get_character_for_slug(parameters[0], guild)

        if char is None:
            await me_error_message(message.channel, "Can't find a character with slug `" + str(parameters[0]) + "` in this guild!")
            return

        await print_character(message.channel, char, True)