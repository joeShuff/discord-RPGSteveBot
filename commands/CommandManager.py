from commands.create.create import *
from commands.help.help import send_help
from commands.set.set import *
from commands.start_end.start_end import *

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

    if message.guild is None:
        await message.channel.send("Please don't PM me, I need to be interacted with in a guild")
        return

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
        from commands.me.me import me_command
        await me_command(message)
    elif command == "set":
        from commands.set.set import run_set
        await run_set(message)
    elif command == "skill":
        from commands.skill.skill import create_new_skill

        if parameters[0] == "create":
            await create_new_skill(message)
        else:
            await message.channel.send("Unknown syntax. Please do `<pref>help skill` to learn more".replace("<pref>", prefix))

    elif command == "check":
        from commands.check.check import perform_skill_check
        await perform_skill_check(message)
    elif command == "stability":
        from commands.stability.stability import do_stability_check
        await do_stability_check(message)
    elif command == "startinit":
        from commands.initiative.initiative import start_initiative
        await start_initiative(message)
    elif command == "endinit":
        from commands.initiative.initiative import end_initiative
        await end_initiative(message)
    elif command == "initiative":
        from commands.initiative.initiative import do_my_initiative
        await do_my_initiative(message)
    elif command == "roll":
        from commands.roll.roll import do_roll
        await do_roll(message)
    elif command == "improve":
        from commands.improve.improve import request_my_improvements
        await request_my_improvements(message)
    elif command == "activate":
        from commands.activation.activation import activate_character
        await activate_character(message)
    elif command == "deactivate":
        from commands.activation.activation import deactivate_character
        await deactivate_character(message)
    elif command == "help":
        try:
            await send_help(bot, message)
        except Exception as e:
            await message.channel.send("Ironically there was a problem sending help, please notify the dev \n```" + str(e) + "```")
    elif command == "start":
        await start_game(message)
    elif command == "end":
        await end_game(message)
    elif command == "xp":
        from commands.xp.xp import do_xp_roll
        await do_xp_roll(message)
    elif command == "invite":
        from commands.invite.invite import invite_link
        await invite_link(message, bot)
    elif command == "mark":
        from commands.mark.mark import mark_skill_for_character
        await mark_skill_for_character(message, True)
    elif command == "unmark":
        from commands.mark.mark import mark_skill_for_character
        await mark_skill_for_character(message, False)
    elif command == "newday":
        from commands.stability.reset_day import do_day_reset
        await do_day_reset(message)
    elif command == "today":
        from commands.stability.today import do_today_command
        await do_today_command(message)
    elif command == "insane":
        from commands.stability.stability import manual_set_insane
        await manual_set_insane(message)
    elif command == "unstable":
        from commands.stability.stability import manual_set_unstable
        await manual_set_unstable(message)
    elif command == "clean":
        deleted = await message.channel.purge(check=message_is_to_do_with_bot, limit=50)
        await message.channel.send('Deleted {} message(s)'.format(len(deleted)), delete_after=10)
