import os
import json

import discord

cwd = os.getcwd()


async def send_help(bot, message):
    from commands.CommandManager import load_commands_and_categories
    from commands.CommandManager import prefix

    parameters = message.content.replace("<pref>help".replace("<pref>", prefix), "").strip().split(" ")

    loaded_commands, loaded_categories = load_commands_and_categories()

    if len(parameters[0]) == 0:
        # loaded_categories = [x for x in loaded_categories if x['show_in_base_help'] != show_hidden_only]

        embed_response = discord.Embed(title="SteveBot Help", description="Hover on command for info", color=0x046EB2)

        for category in loaded_categories:
            cat_value = ""

            for command in loaded_commands:
                if command['category'] == category['name']:
                    cat_value += ("- [**" + str(command['display_name']) + "**](https://github.com/joeShuff/discord-RPGSteveBot/tree/master/commands/" + command['name'] + " '<pref>help " + str(command['name']) + "') `" + str(command['syntax']) + "`\n").replace("<pref>", prefix)

            if len(cat_value) == 0:
                cat_value = "No commands in this category."

            embed_response.add_field(name=category['display_name'], value=cat_value, inline=False)

        await message.channel.send(embed=embed_response)
    else:
        chosen_command = parameters[0]

        found_command = False

        if chosen_command == "gm":
            await send_help(bot, message, True, True)
            return

        for command in loaded_commands:
            if command['name'] == chosen_command:
                found_command = True
                embed_response = discord.Embed(title="Help for " + str(command['display_name']), color=0x046EB2)

                embed_response.add_field(name="Description",
                                         value=str(command['description']) + str(command['long_description']),
                                         inline=False)
                embed_response.add_field(name="Syntax",
                                         value="`" + str(command['syntax']).replace("<pref>", prefix) + "`",
                                         inline=False)

                if len(command['parameters']) > 0:
                    parameter_value = ""

                    for param in command['parameters']:
                        parameter_value += "`<" + str(param['name']) + ">` - " + str(param['description'])

                        if len(param['values']) > 0:
                            parameter_value += " Possible values:\n```\n"

                            for value in param['values']:
                                parameter_value += value + "\n"

                            parameter_value += "```\n"
                        else:
                            parameter_value += "\n"
                    embed_response.add_field(name="Parameters", value=parameter_value)

                embed_response.add_field(name="Example",
                                         value="`" + str(command['example']).replace("<pref>", prefix) + "`",
                                         inline=False)

                for cat in loaded_categories:
                    if cat['name'] == command['category']:
                        embed_response.add_field(name="Category", value=cat['display_name'], inline=False)

                await message.channel.send(embed=embed_response)

        if not found_command:
            pass
