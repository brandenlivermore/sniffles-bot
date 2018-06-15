import discord
from discord.ext import commands
from grandexchange import GrandExchange
from numberformatter import human_format
import sys
import re

dev_environment = 'dev'
prod_environment = 'prod'

environment = None
token = None

def set_environment():
    if len(sys.argv) is not 2:
        sys.exit('run this script with either -dev or -prod')

    global environment
    global token

    if sys.argv[1] == '-dev':
        environment = dev_environment
    elif sys.argv[1] == '-prod':
        environment = prod_environment

    if environment is None:
        sys.exit('you didn\'t specify -dev or -prod')

    if environment == prod_environment:
        token = 'NDE4Njc4NjU4MTkwODAyOTQ0.DXlEow.Tm9Ru4-GKH2-X1rkA9p__8uZ8ls'
    elif environment == dev_environment:
        token = 'NDE5Nzc3MDA3NjU2NjMyMzIw.DX-8GQ.GHoW5mMaIGLkWGXyQgJ637Hq99c'


set_environment()

if environment == dev_environment:
    command_prefix = '!'
elif environment == prod_environment:
    command_prefix = '.'

bot = commands.Bot(command_prefix=command_prefix, description='BigBoyBot D: :P')
ge = GrandExchange()


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='cat'))


@bot.command()
async def price(*, query: str):
    results = ge.items(query)

    text = ''

    length = len(results)

    title = None

    if length == 0:
        title = 'nothing found for that shit'
    elif length != 1:
        title = "{count} results".format(count=length)

    embed = discord.Embed(title=title)

    if length == 1:
        embed.set_thumbnail(url=results[0].icon)
    for result in results:
        embed.add_field(name=result.name,
                        value='`{price}`, change: `{change}`, alch: `{alch_price}`\n'.format(name=result.name,
                                                                                             price=human_format(
                                                                                                 result.price),
                                                                                             change=human_format(
                                                                                                 result.change,
                                                                                                 sign=True),
                                                                                             alch_price=human_format(
                                                                                                 result.alch_price)),
                        inline=False)

    await bot.say(embed=embed)

bot.run(token)
