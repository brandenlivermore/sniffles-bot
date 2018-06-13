import discord
from discord.ext import commands
from grandexchange.grandexchange import GrandExchange
from numberformatter import human_format
from highscores import db
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
    elif length == 1:
        title = results[0].name
    else:
        title = "{count} results".format(count=length)

    embed = discord.Embed(title=title)

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


@bot.command(pass_context=True)
async def stats(ctx):
    id = ctx.message.author.id

    full_message = ctx.message.system_content

    if full_message.strip() == "!stats":
        name = db.get_user_name(id)
    else:
        name = full_message.split(" ", 1)[-1]

    if name is None:
        await bot.say("you have to set your rsn with `!rsn` or specify it after the command")
        return

    result = hiscores.get_all_skills(name)

    embed = highscores_to_embed.skills_result_to_embed(result)
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def rsn(ctx):
    id = ctx.message.author.id

    full_message = ctx.message.system_content
    if not " " in full_message:
        await bot.say("benis you have to put your rsn after this")
        return

    name = full_message.split(" ", 1)[-1]

    if len(name) > 12:
        await bot.say("there's no way your name is that long, {mention}".format(mention=ctx.message.author.mention))
        return

    pattern = re.compile("[a-z|A-Z|0-9|\s]*")

    mention = ctx.message.author.mention

    match = pattern.match(name)

    if not match.group() == name:
        await bot.say("You can't fool Sniffles, {mention}".format(mention=mention))
        return

    result = db.set_user_name(id, name)

    if result == db.SetUserNameResult.Failure:
        await bot.say("Sniffles was unable to set your RSN, {mention}".format(mention=mention))
    elif result == db.SetUserNameResult.FirstTime:
        await bot.say("Sniffles now knows who you are, {mention}".format(mention=mention))
    elif result == db.SetUserNameResult.Update:
        await bot.say("Sniffles knows your new name, {mention}".format(mention=mention))
    elif result == db.SetUserNameResult.Same:
        await bot.say("Sniffles already knows that, you bitch!")

bot.run(token)
