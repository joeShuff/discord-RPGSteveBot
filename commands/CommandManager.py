import os
import json

from commands.help import send_help
from commands.create import *
from commands.set import *

cwd = os.getcwd()

prefix = "?"

bot_user = None

def message_is_to_do_with_bot(m):
    is_command = False

    for command in map(lambda x: x['command'], load_commands()):
        if m.content.startswith(command.replace("<pref>", prefix)):
            is_command = True

    return m.author == bot_user.user or is_command


def load_commands_and_categories():
    with open(cwd + '/commands.json', 'r') as myfile:
        loaded_json = json.loads(myfile.read().replace('\n', ''))
        return loaded_json['commands'], sorted(loaded_json['categories'], key=lambda x: x['order'])


def load_command_categories():
    with open(cwd + '/commands.json', 'r') as myfile:
        loaded_json = json.loads(myfile.read().replace('\n', ''))
        return sorted(loaded_json['categories'], key=lambda x: x['order'])


def load_commands():
    with open(cwd + '/commands.json', 'r') as myfile:
        loaded_json = json.loads(myfile.read().replace('\n', ''))
        return loaded_json['commands']


async def process_command(bot, message):
    global bot_user, prefix
    bot_user = bot
    channel = message.channel

    sender = str(message.author.id)
    guild = str(message.guild.id)

    if not message.content.startswith(prefix):
        return

    message_content = message.content[1:]
    input_command = message_content.split(" ")[0]

    parameters = message_content.split(" ")[1:]

    executed_command = next((x for x in load_commands() if x['name'] == input_command), None)

    if executed_command is None:
        await channel.send("I'm afraid I don't recognise that command. Try `" + str(prefix) + "help`")
        return

    command = executed_command['name']

    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None

    if command == "create":
        if has_gm:
            await create_npc(message, guild, " ".join(parameters))
        else:
            await create_character(message, sender, guild, " ".join(parameters))

    elif command == "me":
        await print_character_for_user(message.channel, sender)
    elif command == "set":
        from commands.set import run_set
        await run_set(message)
    elif command == "skill":
        from commands.skill import print_skill_info, create_new_skill
        if len(parameters) == 1:
            await print_skill_info(message, parameters[0])
        elif len(parameters) == 3:
            await create_new_skill(message)
        else:
            await message.channel.send("Unknown syntax. Please do `<pref>help skill` to learn more".replace("<pref>", prefix))

    elif command == "check":
        from commands.check import perform_skill_check
        await perform_skill_check(message)
    elif command == "help":
        await send_help(bot, message)
    elif command == "clean":
        deleted = await message.channel.purge(check=message_is_to_do_with_bot, limit=50)
        await message.channel.send('Deleted {} message(s)'.format(len(deleted)), delete_after=10)
