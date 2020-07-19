
import time
from db.db_controller import *
from db.printer import *

async def create_character(source_message, owner, guild, name):

    # if user_has_character_in_guild(owner, guild):
    #     existing_character = get_character_for_owner(owner, guild)
    #     await already_has_character_message(source_message.channel, existing_character)
    #     return

    ##Sort out the slug
    def_slug = name.split(" ")[0].lower()
    slug = def_slug
    iter = 1

    while get_character_for_slug(slug, guild) != None:
        slug = def_slug + "_" + str(iter)
        iter += 1

    create_at = str(int(time.time() * 1000))

    char = Character(
        character_name=name,
        character_slug=slug,
        created_at=create_at,
        owner_id=owner,
        guild_id=guild
    )

    add_character_to_db(char, True)

    await print_character_created_at(source_message.channel, create_at)


async def create_npc(source_message, guild, name):
    create_at = str(int(time.time() * 1000))

    char = Character(
        character_name=name,
        created_at=create_at,
        owner_id="NPC",
        guild_id=guild
    )

    add_character_to_db(char)

    await print_character_created_at(source_message.channel, create_at)