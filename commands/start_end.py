from db.db_controller import is_game_active_for_guild, set_game_active_for_guild, end_initiative_in_guild


async def change_state_error_message(channel, message):
    await channel.send(message)


async def start_game(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None

    if not has_gm:
        await change_state_error_message(message.channel, "This command is only for Game Masters!")
        return

    if is_game_active_for_guild(str(message.guild.id)):
        await change_state_error_message(message.channel, "Game is already active in this guild!")
    else:
        set_game_active_for_guild(str(message.guild.id), 1)
        await message.channel.send("Successfully started game in this guild. Have Fun!")


async def end_game(message):
    has_gm = next((x for x in message.author.roles if x.name == "GameMaster"), None) is not None

    if not has_gm:
        await change_state_error_message(message.channel, "This command is only for Game Masters!")
        return

    if is_game_active_for_guild(str(message.guild.id)):
        set_game_active_for_guild(str(message.guild.id), 0)
        end_initiative_in_guild(str(message.guild.id))

        await message.channel.send("Successfully ended the game in this guild. Thanks for playing!")
    else:
        await change_state_error_message(message.channel, "Game is already inactive in this guild!")