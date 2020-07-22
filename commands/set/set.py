from db.db_controller import *

base_stats = {
    "Dexterity": [
        "dex", "dexterity"
    ],
    "Strength": [
        "str", "strength"
    ],
    "Education": [
        "edu", "education"
    ],
    "Power": [
        "pow", "power"
    ],
    "Size": [
        "siz", "size"
    ],
    "Constitution": [
        "con", "constitution"
    ],
    "Appearance": [
        "app", "appearance"
    ],
    "Intelligence": [
        "int", "intelligence"
    ],
    "Speed": [
        "spd", "speed"
    ]
}

##TODO: Make pretty
async def send_set_error(channel, message):
    await channel.send(message)


async def send_set_complete(channel, character, stat, new_val, old_val):
    await channel.send(str(character.character_name) + ": Set " + str(stat) + " from `" + str(old_val) + "` to `" + str(new_val) + "`")


async def run_set(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if has_gm:
        if len(parameters) == 3:
            char = get_character_for_slug(parameters[0], guild)
            skill = parameters[1]
            new_value = parameters[2]

            if char is None:
                await send_set_error(message.channel, "Can't find a character in your guild with the name `" + parameters[0] + "`")
            else:
                await set_stat(message, char, skill, new_value)
        else:
            await send_set_error(message.channel, "Unknown syntax. Please try `?set <char slug> <skill> <value>`")
    else:
        await send_set_error(message.channel, "This command is for Game Masters only!")
        # if len(parameters) == 2:
        #     await set_stat(message, get_character_for_owner(sender, guild), parameters[0], parameters[1])
        # else:
        #     await send_set_error(message.channel, "Unknown syntax. Please do `?help set` for more info.")


async def set_stat(message, character, stat, value):
    stat = stat.lower().strip()

    if not value.isdigit():
        await send_set_error(message.channel, "`" + str(value) + "` is not a valid value silly")
        return

    value = int(value)

    if value < 0 or value > 100:
        await send_set_error(message.channel, "Skill values can only be between 0 and 100.")
        return

    to_set_stat = ""
    original_value = 0

    for key in base_stats.keys():
        if stat in base_stats[key]:
            to_set_stat = key
            original_value = character.get_stat(key.lower())
            from db.db_controller import set_character_stat
            set_character_stat(character, key.lower(), value)
            break

    ##CHECK NONE MAIN STATS
    from db.db_controller import get_skills_for_character, set_skill
    other_skills = get_skills_for_character(character.id)

    for skill in other_skills:
        if stat == skill.skill_name.lower():
            to_set_stat = skill.skill_name
            original_value = get_skill(character.id, to_set_stat)
            set_skill(character.id, to_set_stat, value)
            break

    if to_set_stat != "":
        await send_set_complete(message.channel, character, to_set_stat, value, original_value)
    else:
        await send_set_error(message.channel, "Cannot find stat for value `" + str(stat) + "`. If you want to create a custom skill try `?skill create <skill name> <default value, default = 10> <modifier, default = NON>`")
