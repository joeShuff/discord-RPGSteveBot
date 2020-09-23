from db.db_controller import *
from commands.roll.roll import *

xp_to_level = {
    0: 1,
    70: 2,
    160: 3,
    270: 4,
    400: 5,
    550: 6,
    720: 7,
    910: 8,
    1120: 9,
    1350: 10,
    1600: 11,
    1870: 12,
    2160: 13,
    2470: 14,
    2820: 15,
    3190: 16
}

async def xp_error_message(channel, message):
    await channel.send(message)


async def do_xp_roll(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.clean_content[1:]
    mentioned = message.mentions

    if message.mention_everyone:
        message_content = message_content.replace("@​everyone", "")

        for person in message.guild.members:
            if not person.bot and person not in mentioned:
                mentioned.append(person)

    for mention in mentioned:
        message_content = message_content.replace("@" + str(mention.display_name), "")

    parameters = message_content.strip().split(" ")[1:]
    roll = "".join(parameters)

    is_game_active = is_game_active_for_guild(str(message.guild.id))

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not is_game_active:
        await xp_error_message(message.channel, "The game in this guild isn't active right now.")
        return

    if has_gm:
        if len(parameters) == 0:
            await xp_error_message(message.channel, "Please include a dice format to roll. e.g. 6d9+7")
            return
        else:
            try:
                num_of_dice, dice_type, modifier = parse_dice_roll(roll)
                roll_result, total = roll_hit(num_of_dice, dice_type, modifier)
            except Exception as e:
                await xp_error_message(message.channel, "Something went wrong rolling the dice " + str(roll)  + ".\n Error is:\n" + str(e))
                return

            embed = discord.Embed(title="XP Roll - " + str(roll), color=0x0000ff)
            embed.add_field(name="Result", value="`" + str(roll) + " = " + str(roll_result) + "`")

            characters = []

            for mention in mentioned:
                get_char = get_character_for_owner(mention.id, guild)

                if get_char is not None:
                    print("Found " + str(get_char.character_name) + " for " + str(mention.display_name))
                    characters.append(get_char)

            if len(characters) == 0:
                await xp_error_message(message.channel, "Found 0 characters. Please mention people to give XP to. Or use `@everyone`")
                return

            char_xp = []

            for char in characters:
                pre_xp, new_xp = await add_xp(char, total, message.channel)
                char_xp.append(char.character_name + " - `" + str(pre_xp) + " -> " + str(new_xp) + "`")

            embed.add_field(name="Characters getting XP", value = "\n".join(char_xp))

            await message.channel.send(embed=embed)
    else:
        await xp_error_message(message.channel, "This command is only for GMs")
