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


@bot.group(pass_context=True)
async def keyword(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say(
            'You can\'t use keyword on its own. Try `.keyword add bandos "bandos chestplate"` or `.keyword remove bandos` or `.keyword name bandos "Bandos stuff"`')


def validate_quoted_item_name(name):
    pattern = re.compile('"([^"]*)"')

    match = pattern.match(name)

    return match and match.group() == name


@keyword.command(pass_context=True)
async def remove(ctx, keyword: str, *, name: str):
    user_id = ctx.message.author.id

    valid_name = validate_quoted_item_name(name)

    if not valid_name:
        await bot.say('You didn\'t use this right. example: `.keyword name bullshit "bandos stuff"`')
        return

    name = name.replace('"', '')

    success = ge.remove_keyword(user_id, keyword)

    if success:
        await bot.say('removed "{name}" from {keyword}'.format(keyword=keyword,
                                                               name=name))
    else:
        await bot.say('"{name}" not found or keyword {keyword} doesn\'t exist'.format(keyword=keyword,
                                                                                      name=name))


@keyword.command(pass_context=True)
async def delete(ctx, keyword: str):
    user_id = ctx.message.author.id

    success = ge.remove_keyword(user_id, keyword)

    if success:
        await bot.say('Successfully removed keyword {keyword}'.format(keyword=keyword))
    else:
        await bot.say('Could not remove unknown keyword {keyword}'.format(keyword=keyword))


@keyword.command(pass_context=True)
async def name(ctx, keyword: str, *, name: str):
    user_id = ctx.message.author.id

    valid_name = validate_quoted_item_name(name)

    if not valid_name:
        await bot.say('You didn\'t use this right. example: `.keyword name bullshit "bandos stuff"`')
        return

    name = name.replace('"', '')

    success = ge.set_name_for_keyword(user_id, keyword, name)

    if success:
        await bot.say('keyword group {keyword} is now named "{name}"'.format(keyword=keyword,
                                                                             name=name))
    else:
        await bot.say('keyword {keyword} not found'.format(keyword=keyword))


@keyword.command(pass_context=True)
async def add(ctx, keyword: str, *, item: str):
    user_id = ctx.message.author.id
    pattern = re.compile('"(\s|[a-z]|\)|\(|\d|\'){3,}"')

    match = pattern.match(item)

    if not match or match.group() != item:
        await bot.say('You didn\'t use this right. example: `.keyword add bullshit "bandos godsword"`')
        return

    item = item.replace('"', '')

    success, items = ge.set_keyword_for_item(user_id, keyword, item)

    if not success:
        await bot.say('unable to find "{item}"'.format(item=item))

    items_str = ", ".join(items)

    await bot.say('{keyword} now contains '.format(keyword=keyword) + items_str)


@bot.command(pass_context=True)
async def price(ctx, *, query: str):
    # query = ctx.message.content
    # query.replace(command_prefix + 'price', '')
    # query = query.strip()
    user_id = ctx.message.author.id
    group_name, results = ge.items(user_id, query)

    text = ''

    length = len(results)

    title = None

    if group_name is not None:
        title = group_name
    elif length == 0:
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
