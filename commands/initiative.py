from db.db_controller import *
from random import randrange
import discord

def myFunc(e):
  return e.roll_result

async def send_initiative_error_message(channel, message):
    await channel.send(message)  ##TODO MAKE PRETTY


def get_initiative_embed_for_guild(guild, override_end=False, title_override=None):
    roll_result_text = ""
    initiative_results = get_initiative_results_for_guild(guild)
    initiative_results.sort(key=myFunc, reverse=True)

    initiative_title = get_initiative_title_for_guild(guild)

    if title_override is not None:
        initiative_title = title_override

    for roll in initiative_results:
        character = get_character_for_id(roll.character_id, guild)

        owner = character.owner_id

        if owner != "NPC":
            owner = "<@!" + str(owner) + ">"

        roll_result_text += str(roll.init_result) + " - " + str(character.character_name) + " (" + str(owner) + ")\n"

    initiative_status = "Active"
    color = 0x00ff00

    if len(roll_result_text) == 0:
        roll_result_text = "No Rolls Yet..."

    if is_initiative_complete_for_guild(guild) or override_end:
        initiative_status = "Inactive"
        color = 0xff0000

    embed = discord.Embed(title="Initiative Rolls - " + initiative_title, color=color)
    embed.add_field(name="Rolls", value=roll_result_text, inline=False)
    embed.add_field(name="Status", value=initiative_status, inline=False)

    return embed


async def update_initiative_message(message, override_end=False):
    guild = str(message.guild.id)
    existing_message = get_initiative_message_id_for_guild(guild)
    existing_message = await message.channel.fetch_message(existing_message)
    await existing_message.edit(embed=get_initiative_embed_for_guild(guild, override_end))

    close_initiative_if_complete_in_guild(guild)


async def start_initiative(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None

    sender = str(message.author.id)
    guild = str(message.guild.id)

    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    title = " ".join(parameters)

    if not is_game_active_for_guild(guild):
        await send_initiative_error_message(message.channel, "The game in this guild isn't active right now!")
        return

    if not has_gm:
        await send_initiative_error_message(message.channel, "This command is only for Game Masters!")
        return

    if is_initiative_active_in_guild(guild):
        await send_initiative_error_message(message.channel, "Initiative is already active in this guild!")
        return

    initiative_message = await message.channel.send(embed=get_initiative_embed_for_guild(guild, title_override=title))

    start_initiative_in_guild(guild, initiative_message.id, title)
    await message.channel.send("Initiative is now active! All players do `?initiative` and GMs can roll for NPCs. `?initiative <slug>`.")


async def end_initiative(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not is_game_active_for_guild(guild):
        await send_initiative_error_message(message.channel, "The game in this guild isn't active right now!")
        return

    if not has_gm:
        await send_initiative_error_message(message.channel, "This command is only for Game Masters!")
        return

    if not is_initiative_active_in_guild(guild):
        await send_initiative_error_message(message.channel, "Initiative is already inactive in this guild!")
        return

    await update_initiative_message(message, override_end=True)
    end_initiative_in_guild(guild)
    await message.channel.send("Initiative has been ended!")


async def do_my_initiative(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not is_initiative_active_in_guild(guild):
        await send_initiative_error_message(message.channel, "There is no active initiative stage in this guild.")
        return

    character = None

    has_adv = False
    has_dis = False

    if not has_gm:
        character = get_character_for_owner(sender, guild)

        if len(parameters) >= 1:
            has_adv = parameters[0].lower() == "a"
            has_dis = parameters[0].lower() == "d"
    else:
        if len(parameters) == 0:
            await send_initiative_error_message(message.channel, "As a game master you can roll initiative for any character. Do ?initiative <slug> <a | d>")
            return
        else:
            if len(parameters) >= 2:
                has_adv = parameters[1].lower() == "a"
                has_dis = parameters[1].lower() == "d"

            character = get_character_for_slug(parameters[0], guild)

            if character is None:
                await send_initiative_error_message(message.channel, "Can't find a character for slug `" + str(parameters[0]) + "`")
                return

    if character is None:
        await send_initiative_error_message(message.channel, "You don't have a character to roll initiative for")
        return

    if character_has_initiative_in_guild(character.id, guild):
        await send_initiative_error_message(message.channel, "You already have initiative in this guild!")
        return

    roll = randrange(1, character.speed)
    ad_dis_roll = randrange(1, character.speed)

    roll_output_text = str("`d" + str(character.speed) + "` = " + str(roll))
    chosen_roll_result = roll

    if has_adv:
        if roll > ad_dis_roll:
            roll_output_text = str("`d" + str(character.speed) + "` = " + str(roll) + " ~~" + str(ad_dis_roll) + "~~")
        else:
            roll_output_text = str("`d" + str(character.speed) + "` = ~~" + str(roll) + "~~ " + str(ad_dis_roll))
            chosen_roll_result = ad_dis_roll
    elif has_dis:
        if roll < ad_dis_roll:
            roll_output_text = str("`d" + str(character.speed) + "` = " + str(roll) + " ~~" + str(ad_dis_roll) + "~~")
        else:
            roll_output_text = str("`d" + str(character.speed) + "` = ~~" + str(roll) + "~~ " + str(ad_dis_roll))
            chosen_roll_result = ad_dis_roll

    add_character_initiative_to_guild(guild, character.id, roll_output_text, chosen_roll_result)

    await update_initiative_message(message)
    await message.delete()
