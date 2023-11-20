import discord
import os
import asyncio
import json
from aiofiles import open as aopen
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("SERVER_LINK_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='?', case_insensitive=True, activity=discord.Streaming(name='Across the Server-verse', url="https://unseeyou.pages.dev"))


class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, title='HELP')
            await destination.send(embed=emby)


bot.help_command = MyNewHelp()


@bot.event
async def on_ready():
    print(f'Logged in/Rejoined as {bot.user} (ID: {bot.user.id})')
    print(
        f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=applications.commands%20bot")
    print('------ Error Log ------')


@bot.event
async def setup_hook():
    print("If you are seeing this then unseeyou's epic bot is working!")


@bot.event
async def on_message(message: discord.Message):
    if message.content[0] == '?':  # ignore bots and commands
        await bot.process_commands(message)
        return 0
    if message.author.bot:
        return 0
    async with aopen('rooms.json', 'r') as f:
        data = await f.read()
        data = json.loads(data)
    for room in data:
        channels: list = data[room]
        for channel_id in channels:
            if message.channel.id in channels and message.channel.id != int(channel_id):
                channel = bot.get_channel(int(channel_id))
                webhooks = await channel.webhooks()
                if len(webhooks) == 0 or 'server link' not in [w.name for w in webhooks]:
                    webhook = await channel.create_webhook(name='server link')
                else:
                    for hook in webhooks:
                        if hook.name == 'server link':
                            webhook = hook
                await webhook.send(str(message.content),
                                   username=f"[{message.guild.name}] {message.author.display_name}",
                                   avatar_url=message.author.display_avatar.url,
                                   silent=True)

@bot.hybrid_command(help='probably my ping', name='ping')
async def _ping(ctx: commands.Context):
    latency = round(bot.latency*1000, 2)
    message = await ctx.send("Pong!")
    await message.edit(content=f"Pong! My ping is `{latency} ms`")
    print(f'Ping: `{latency} ms`')


@bot.command()
@commands.is_owner()
async def sync(ctx):
    await ctx.typing()
    await bot.tree.sync(guild=None)  # global sync
    await ctx.send('Synced CommandTree!')


async def main():
    async with bot:
        await bot.load_extension("cogs.server-link-cmds")
        await bot.start(TOKEN)


asyncio.run(main())
