from db.db_controller import *
from commands.roll.roll import *
from random import randrange


async def stability_error_message(channel, message):
    await channel.send(message)


async def notify_unstable(channel, character, unstable=True):
    message = character.character_name + " became unstable!"

    if not unstable:
        message = character.character_name + " became stable again!"

    embed = discord.Embed(title=message, color=0xff0000)
    await channel.send(embed=embed)


async def notify_insane(channel, character, insane=True):
    message = character.character_name + " went insane!"

    if not insane:
        message = character.character_name + " is sane again! (for now)"

    embed = discord.Embed(title=message, color=0xff0000)
    await channel.send(embed=embed)


async def do_stability_check_for_character(message, character, roll_string):
    stability_check = randrange(1, 100)
    passed_stability = stability_check < character.stability_curr

    failed_roll_result = ""
    failed_roll_total = 0

    result_color = 0xff0000
    result_string = "Failed!"

    if passed_stability:
        result_string = "Passed!"
        result_color = 0x00ff00

    try:
        num_of_dice, dice_type, modifier = parse_dice_roll(roll_string)
        failed_roll_result, failed_roll_total = roll_hit(num_of_dice, dice_type, modifier)

        if failed_roll_total < 0:
            failed_roll_result = failed_roll_result + "\nMinimum value is 0, so no damage inflicted."

        failed_roll_total = max(0, failed_roll_total)

    except ValueError as e:
        await stability_error_message(message.channel,
                                      "Something went wrong parsing your dice roll of `" + roll_string + "`\n" + str(e))
        return

    new_stability = max(0, character.stability_curr - failed_roll_total)

    if not passed_stability:
        set_character_stability(character, new_stability)
    else:
        new_stability = character.stability_curr

    embed = discord.Embed(title=character.character_name + "'s Stability Check",
                          color=result_color)

    stability_lost_today = abs(character.start_of_day_stability - new_stability)
    percentage_stab_lost_today = (float(stability_lost_today) / float(character.start_of_day_stability) * 100.0)

    dice_url = "https://raw.githubusercontent.com/joeShuff/discord-RPGSteveBot/master/art/dice/d{amount}.png"
    embed.set_thumbnail(url=dice_url.replace("{amount}", str(stability_check)))

    embed.add_field(name="Current Stability", value=str(character.stability_curr), inline=True)
    embed.add_field(name="Rolled", value=str(stability_check), inline=True)
    embed.add_field(name="Result", value=result_string, inline=False)

    if not passed_stability:
        embed.add_field(name="Mental Damage", value=roll_string + " = " + failed_roll_result, inline=True)
        embed.add_field(name="New Stability Level", value=str(new_stability), inline=True)
        embed.add_field(name="Stability Damage Today", value=str(stability_lost_today) + " (" + ("%.2f" % percentage_stab_lost_today) + "%)",inline=False)

    embed.set_footer(text="rolled using SteveBot",
                     icon_url="https://cdn.discordapp.com/avatars/731917492498333767/30d2df49893355093a5a1bfc52ca175e.webp?size=1024")

    await message.channel.send(embed=embed)

    if character.unstable == 0 and (15.0 <= percentage_stab_lost_today < 30.0):
        set_unstable(character, True)
        await notify_unstable(message.channel, character)
    elif character.insane == 0 and (percentage_stab_lost_today >= 30.0):
        set_insanity(character, True)
        await notify_insane(message.channel, character)


async def do_stability_check(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    is_game_active = is_game_active_for_guild(str(message.guild.id))

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not is_game_active:
        await stability_error_message(message.channel, "The game in this guild isn't active right now.")
        return

    if has_gm:
        if len(parameters) < 2:
            await stability_error_message(message.channel,
                                          "Please include a dice format to roll and a character to target as you are a GM.")
            return
        else:
            character = get_character_for_slug(parameters[0], guild)

            roll = "".join(parameters[1:])

            if character is None:
                await stability_error_message(message.channel,
                                              "Can't find a character with slug `" + parameters[0] + "` in this guild.")
            else:
                await do_stability_check_for_character(message, character, roll)
    else:
        if len(parameters) == 0:
            await stability_error_message(message.channel, "Please include a dice format to roll. e.g. 12d10+5")
            return
        else:
            character = get_character_for_owner(sender, guild)

            roll = "".join(parameters)

            if character is None:
                await stability_error_message(message.channel, "You don't have a character in this guild")
            else:
                await do_stability_check_for_character(message, character, roll)


async def manual_set_unstable(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    is_game_active = is_game_active_for_guild(str(message.guild.id))

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not has_gm:
        await stability_error_message(message.channel, "This command is for GMs only")
        return
    else:
        if len(parameters) < 2:
            await stability_error_message(message.channel, "Please include a character to target and whether to set unstable or not, as you are a GM.")
            return
        else:
            character = get_character_for_slug(parameters[0], guild)

            setter = "".join(parameters[1:])

            if character is None:
                await stability_error_message(message.channel, "Can't find a character with slug `" + parameters[0] + "` in this guild.")
            else:
                try:
                    bool_unstable = setter.lower().strip() == "true"
                    set_unstable(character, bool_unstable)
                    await notify_unstable(message.channel, character, bool_unstable)
                except:
                    await stability_error_message(message.channel, "Please either type `true` or `false` to set unstability")


async def manual_set_insane(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not has_gm:
        await stability_error_message(message.channel, "This command is for GMs only")
        return
    else:
        if len(parameters) < 2:
            await stability_error_message(message.channel, "Please include a character to target and whether to set insane or not, as you are a GM.")
            return
        else:
            character = get_character_for_slug(parameters[0], guild)

            setter = "".join(parameters[1:])

            if character is None:
                await stability_error_message(message.channel, "Can't find a character with slug `" + parameters[0] + "` in this guild.")
            else:
                try:
                    bool_insane = setter.lower().strip() == "true"
                    set_insanity(character, bool_insane)
                    await notify_insane(message.channel, character, bool_insane)
                except Exception as e:
                    print(e)
                    await stability_error_message(message.channel, "Please either type `true` or `false` to set insanity")
