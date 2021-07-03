from db.db_controller import *

from db.printer import *


async def me_error_message(context, message):
    await context.send(message)


async def me_command(ctx, character: str = None):
    has_gm = next((x for x in ctx.author.roles if x.name == "GameMaster"), None) is not None

    sender = str(ctx.author.id)
    guild = str(ctx.guild.id)

    if not has_gm:
        char = get_character_for_owner(sender, guild)

        if char is None:
            await me_error_message(ctx, "Can't find a character for you in this guild!")
            return

        await print_character(ctx, char, True)
    else:
        if character is None:
            await me_error_message(ctx, "Please enter a slug to get character info for.")
            return

        char = get_character_for_slug(character, guild)

        if char is None:
            await me_error_message(ctx, "Can't find a character with slug `" + str(character) + "` in this guild!")
            return

        await print_character(ctx, char, True)
