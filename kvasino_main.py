import disnake
import config
from disnake.ext import commands

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all())


@bot.event
async def on_ready():
    print("Бот готов!")


@bot.command(name="msg")
async def msg(ctx):
    if ctx.author.id == 295505464420990986:
        await ctx.send('Пук')

bot.load_extensions('cogs')
bot.run(config.TOKEN)
