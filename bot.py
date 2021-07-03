import discord

from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType, SlashCommandOptionType
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

import os
from commands.CommandManager import process_command
from db.db_controller import create_game_if_not_in_guild

# TEST INVITE
# https://discord.com/oauth2/authorize?client_id=406021841354752010&permissions=4231523696&scope=bot%20applications.commands

# INVITE
#

cwd = os.getcwd()
bot = Bot(command_prefix="/", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

guilds = []

TEST_BOT = True

def to_guild_id(g):
    return g.id


async def create_permissions(guild):
    try:
        gm_role = next((x for x in guild.roles if x.name == "GameMaster"), None)
        player_role = next((x for x in guild.roles if x.name == "Explorer"), None)

        if gm_role is None:
            await guild.create_role(name="GameMaster", color=discord.Color(0xff9000),
                                    reason="Used to manage SteveBot permissions")

        if player_role is None:
            await guild.create_role(name="Explorer", color=discord.Color(0x009929),
                                    reason="Used to manage SteveBot permissions")
    except Exception as e:
        from git.github_connection import report_error_to_repo
        report_error_to_repo(bot, e)


@bot.event
async def on_ready():
    try:
        print("on READY")
        await bot.change_presence(status=discord.Status.online,
                                  activity=discord.Game(name=" Minecraft RPG"))

        for guild in bot.guilds:
            create_game_if_not_in_guild(guild)
            await create_permissions(guild)

            guilds.append({
                "id": guild.id,
                "game_master": next((x for x in guild.roles if x.name == "GameMaster"), None),
                "explorer": next((x for x in guild.roles if x.name == "Explorer"), None)
            })

    except Exception as e:
        if TEST_BOT:
            raise e
        else:
            from git.github_connection import report_error_to_repo
            report_error_to_repo(bot, e)


@bot.event
async def on_guild_join(guild):
    try:
        print("Joined a guild")
        create_game_if_not_in_guild(guild)
        await create_permissions(guild)
    except Exception as e:
        if TEST_BOT:
            raise e
        else:
            from git.github_connection import report_error_to_repo
            report_error_to_repo(bot, e)


@bot.event
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        ##If it's the live bot on the test server, ignore!
        if message.guild is not None:
            if str(message.guild.id) == "403277441650393099" and str(bot.user.id) == "731917492498333767":
                return

        await process_command(bot, message)
    except Exception as e:
        if TEST_BOT:
            raise e
        else:
            from git.github_connection import report_error_to_repo
            issue = report_error_to_repo(bot, e)

            if issue is not None:
                embed = discord.Embed(title="Error", color=0xff0000, description=
                "Something went wrong, issue reported to github [here](" + issue.html_url + ")")

                await message.channel.send(embed=embed)


@bot.event
async def on_raw_reaction_add(payload):
    try:
        channel = await bot.fetch_channel(payload.channel_id)
        user = await channel.guild.fetch_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        if payload.user_id == bot.user.id:
            return

        from commands.improve.improve import check_improvements_from_reaction
        await check_improvements_from_reaction(payload.emoji, user, message)
    except Exception as e:
        if TEST_BOT:
            raise e
        else:
            from git.github_connection import report_error_to_repo
            report_error_to_repo(bot, e)


@slash.slash(name="me",
             description="View your characters info",
             guild_ids=map(to_guild_id, guilds),
             options=[
                 create_option(
                     name="character",
                     description="Slug for the character to display.",
                     option_type=SlashCommandOptionType.STRING,
                     required=False
                 )
             ])
async def me(ctx: SlashContext, character: str = None):
    from commands.me.me import me_command
    await me_command(ctx, character)


@slash.slash(name="set",
             description="Set a skills value",
             guild_ids=map(to_guild_id, guilds),
             permissions={
                 "403277441650393099": [
                     create_permission(713152671401508865, SlashCommandPermissionType.ROLE, True)
                 ]
             })
async def set(ctx: SlashContext):
    from commands.set.set import run_set
    await run_set(ctx.message)


token = ""
token_file = "/token.txt"

if TEST_BOT:
    token_file = "/test_bot_token.txt"

with open(cwd + token_file, 'r') as myfile:
    token = myfile.read().replace('\n', '')

# client.loop.create_task(Poll.update_polls(client))
bot.run(token)
