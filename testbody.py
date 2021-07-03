import discord
import os
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

TEST_BOT = True
cwd = os.getcwd()


@slash.slash(name="test", description="A test slash command")
async def test(ctx: SlashContext):
    # embed = discord.Embed(title="embed test")
    # await ctx.send(content="test", embeds=[embed])
    await ctx.send("it worked")


@slash.slash(name="hello", description="Say hi")
async def hello(ctx: SlashContext):
    await ctx.send("well hello there")


token = ""
token_file = "/token.txt"

if TEST_BOT:
    token_file = "/test_bot_token.txt"

with open(cwd + token_file, 'r') as myfile:
    token = myfile.read().replace('\n', '')

bot.run(token)
