import discord, json, traceback, typing
from discord.ext import commands
from discord import app_commands
from aiofiles import open as aopen

def load_valid_arguments():
    with open('rooms.json', 'r') as f:
        return json.load(f)

def create_argument_type():
    VALID_ARGUMENTS = [i for i in load_valid_arguments()]
    Argument = typing.Literal[tuple(VALID_ARGUMENTS)]
    return Argument

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="link_channel", description="link the current channel")
    async def server(self, interaction: discord.Interaction, room: str):
        await interaction.response.defer(thinking=True)
        if interaction.user.guild_permissions.administrator:
            await interaction.followup.send(f'linking the server to {room}...')
            try:
                async with aopen('rooms.json', 'r') as f:
                    data = await f.read()
                    data = json.loads(data)
                    if room in data:
                        if interaction.channel.id not in data[room]:
                            data[room].append(interaction.channel.id)  # idk lol
                    else:
                        data[room] = [interaction.channel.id]
                async with aopen('rooms.json', 'w') as f:
                    await f.seek(0)
                    await f.write(json.dumps(data, indent=4))
                msg = await interaction.original_response()
                await msg.edit(content=f'linking the server to {room}... done!')
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                msg = await interaction.original_response()
                await msg.edit(content=f'linking to room... failed! {str(type(e))}: {str(e)}')
        else:
            await interaction.followup.send("You don't have the required permissions to use this command. (administrator)")

    @server.autocomplete('room')
    async def autocomplete(self, interaction: discord.Interaction, current: str) -> typing.List[
        app_commands.Choice[str]]:
        VALID_ARGUMENTS = [i for i in load_valid_arguments()]
        return [app_commands.Choice(name=i, value=i) for i in VALID_ARGUMENTS if current.lower() in i.lower()]

    @app_commands.command(name="unlink_channel", description="unlink your current channel from all other servers")
    async def unlink_server(self, interaction: discord.Interaction, room: str = None):
        await interaction.response.defer(thinking=True)
        if interaction.user.guild_permissions.administrator:
            channel = interaction.channel
            if channel is not None:
                await interaction.followup.send(f'unlinking {channel.guild.name}>#{channel.name}...')
                try:
                    async with aopen('rooms.json', 'r') as f:
                        data = await f.read()
                        data = json.loads(data)
                        if room is None:
                            for r in data:
                                if channel.id in data[r]:
                                    data[r].remove(channel.id)
                                    if len(data[r]) == 0:
                                        del data[r]
                        else:
                            data[room].remove(channel.id)
                            if len(data[room]) == 0:
                                del data[room]
                    async with aopen('rooms.json', 'w') as f:
                        await f.seek(0)
                        await f.write(json.dumps(data, indent=4))
                    msg = await interaction.original_response()
                    await msg.edit(content=f'unlinking {channel.guild.name}>#{channel.name}... done!')
                except Exception as e:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    msg = await interaction.original_response()
                    await msg.edit(content=f'unlinking {channel.guild.name}>#{channel.name}... failed! {type(e)}: {str(e)}')

    @unlink_server.autocomplete('room')
    async def autocomplete(self, interaction: discord.Interaction, current: str) -> typing.List[
        app_commands.Choice[str]]:
        VALID_ARGUMENTS = [i for i in load_valid_arguments()]
        return [app_commands.Choice(name=i, value=i) for i in VALID_ARGUMENTS if current.lower() in i.lower()]


async def setup(bot):
    await bot.add_cog(Commands(bot))
