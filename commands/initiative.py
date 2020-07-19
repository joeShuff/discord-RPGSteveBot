from db.db_controller import get_characters_in_guild
from random import randrange
import discord

def myFunc(e):
  return e['roll']

async def send_initiative_error_message(channel, message):
    await channel.send(message)  ##TODO MAKE PRETTY


async def do_initiative(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not has_gm:
        await send_initiative_error_message(message.channel, "This command is for Game Masters only.")
        return

    initiative_rolls = []

    for char in get_characters_in_guild(guild, True):
        roll = randrange(1, char.speed)

        owner = char.owner_id

        if owner != "NPC":
            owner = "<@!" + str(owner) + ">"

        initiative_rolls.append({
            'name': char.character_name,
            'roll': "d" + str(char.speed) + " = " + str(roll),
            'owner': owner
        })

    initiative_rolls.sort(key=myFunc, reverse=True)

    embed = discord.Embed(title="Initiative Rolls",
                          color=0xff0000)

    roll_result_text = ""
    for roll in initiative_rolls:
        roll_result_text += "`" + str(roll['roll']) + "` - " + str(roll['name']) + " (" + str(roll['owner']) + ")\n"

    embed.add_field(name="Rolls", value=roll_result_text)

    await message.channel.send(embed=embed)
