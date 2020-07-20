from discord.ext import tasks
import discord
from discord.ext.commands import Bot
import os

from commands.CommandManager import process_command
from db.db_controller import create_game_if_not_in_guild

import time

cwd = os.getcwd()
bot = Bot(":")


async def create_permissions(guild):
    gm_role = next((x for x in guild.roles if x.name == "GameMaster"), None)
    player_role = next((x for x in guild.roles if x.name == "Explorer"), None)

    if gm_role is None:
        await guild.create_role(name="GameMaster", color=discord.Color(0xff9000),
                                reason="Used to manage SteveBot permissions")

    if player_role is None:
        await guild.create_role(name="Explorer", color=discord.Color(0x009929),
                                reason="Used to manage SteveBot permissions")


@bot.event
async def on_ready():
    print("on READY")
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(name="you"))

    for guild in bot.guilds:
        create_game_if_not_in_guild(guild)
        await create_permissions(guild)


@bot.event
async def on_guild_join(guild):
    print("Joined a guild")
    create_game_if_not_in_guild(guild)
    await create_permissions(guild)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    ##If it's the live bot on the test server, ignore!
    if message.guild is not None:
        if str(message.guild.id) == "403277441650393099" and str(bot.user.id) == "731917492498333767":
            return

    await process_command(bot, message)


token = ""
# with open(cwd + '/token.txt', 'r') as myfile:
with open(cwd + '/test_bot_token.txt', 'r') as myfile:
    token = myfile.read().replace('\n', '')

# client.loop.create_task(Poll.update_polls(client))
bot.run(token)
