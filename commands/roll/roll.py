from random import randint
import discord


async def roll_error_message(channel, message):
    await channel.send(message)


#### Rolling Code taken from https://github.com/Chaithi/Discord-Dice-Roller-Bot

# Determines if the value can be converted to an integer
# Parameters: s - input string
# Returns: boolean. True if can be converted, False if it throws an error.
def is_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# Rolls a set of die and returns either number of hits or the total amount
# Parameters: num_of_dice [Number of dice to roll], dice_type[die type (e.g. d8, d6),
# modifier [amount to add to/subtract from total],
# Returns: String with results
def roll_hit(num_of_dice, dice_type, modifier):
    results = "("
    total = 0

    for x in range(0, int(num_of_dice)):
        y = randint(1, int(dice_type))
        results += str(y) + " + "
        total += y

    results = results[:-3] + ") "

    total += int(modifier)

    if modifier != 0:
        if modifier > 0:
            results += "+ " + str(modifier)
        else:
            results += "- " + str(abs(modifier))

    results += " = " + str(total)

    if num_of_dice >= 20:
        if modifier != 0:
            if modifier > 0:
                return "lots of rolls + " + str(abs(modifier)) + " = " + str(total), total
            else:
                return "lots of rolls - " + str(abs(modifier)) + " = " + str(total), total
        else:
            return "lots of rolls = " + str(total), total
    else:
        return results, total


# Takes in a string representation of a roll
# outputs 3 parameters
# number of dice, dice_type, modifier
# self explanatory, d5 for example, +5 for example
def parse_dice_roll(roll):
    modifier, num_of_dice, dice_type = 0, 0, 0

    if roll.find('+') != -1:
        roll, modifier = roll.split('+')
    elif roll.find('-') != -1:
        roll, modifier = roll.split('-')
        modifier = '-' + modifier

    if roll.find('d') != -1:
        num_of_dice, dice_type = roll.split('d')

    if modifier == 0 and num_of_dice == 0 and dice_type == 0:
        raise ValueError("Invalid dice format, try something like 6d9+1")
        return

    #Validate data
    if len(str(num_of_dice)) == 0:
        num_of_dice = "1"

    if modifier != 0:
        if is_num(modifier) is False:
            raise ValueError("Modifier value format error. Proper usage 1d4+1")
            return
        else:
            modifier = int(modifier)

    if num_of_dice != 0:
        if is_num(num_of_dice) is False:
            raise ValueError("Number of dice format error. Proper usage 3d6")
            return
        else:
            num_of_dice = int(num_of_dice)

    if num_of_dice > 200:
        raise ValueError("Too many dice. Please limit to 200 or less.")
        return

    if dice_type != 0:
        if is_num(dice_type) is False:
            raise ValueError("Dice type format error. Proper usage 3d6")
            return
        else:
            dice_type = int(dice_type)

    return num_of_dice, dice_type, modifier


async def do_roll(message):
    message_content = message.content[1:]
    parameters = message_content.split(" ")[1:]

    if len(parameters) == 0:
        await roll_error_message(message.channel, "Please include a dice format to roll. e.g. 12d10+5")
        return

    roll = "".join(parameters)

    try:
        num_of_dice, dice_type, modifier = parse_dice_roll(roll)

        roll_result, total = roll_hit(num_of_dice, dice_type, modifier)
        embed = discord.Embed(title="Dice Roll " + str(num_of_dice) + "d" + str(dice_type), color=0x0000ff)
        embed.add_field(name="Results", value=roll_result)
        embed.add_field(name="Roller", value=message.author.mention)

        if 100 >= total > 0:
            dice_url = "https://raw.githubusercontent.com/joeShuff/discord-RPGSteveBot/master/art/dice/d{amount}.png"
            embed.set_thumbnail(url=dice_url.replace("{amount}", str(total)))

        await message.channel.send(embed=embed)
    except ValueError as err:
        # Display error message to channel
        await roll_error_message(message.channel, "Something went wrong\n`" + str(err) + "`")
