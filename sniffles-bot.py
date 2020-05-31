import discord
from discord.ext import commands
from grandexchange import GrandExchange
from numberformatter import human_format
from messagetrolling import MessageTroller
import sys
import re
from datetime import datetime

dev_environment = 'dev'
prod_environment = 'prod'

environment = None
token = None

def set_environment():
    if len(sys.argv) is not 3:
        sys.exit('you must run this passing -dev or -prod followed by the token')

    global environment
    global token

    if sys.argv[1] == '-dev':
        environment = dev_environment
    elif sys.argv[1] == '-prod':
        environment = prod_environment

    token = sys.argv[2]


set_environment()

if environment == dev_environment:
    command_prefix = '!'
elif environment == prod_environment:
    command_prefix = '.'

bot = commands.Bot(command_prefix=command_prefix, description='BigBoyBot D: :P')
ge = GrandExchange()

chris_icon_url = 'https://scontent-sea1-1.xx.fbcdn.net/v/t1.0-9/p960x960/34054290_2145152178834520_6807100509313302528_o.jpg?_nc_cat=109&_nc_sid=85a577&_nc_ohc=lKlMyo09c-cAX-lOZgv&_nc_ht=scontent-sea1-1.xx&_nc_tp=6&oh=a42c17714b2ed818299c7c5753691e55&oe=5EF56B65'

@bot.group(pass_context=True)
async def keyword(ctx):
    channel = ctx.message.channel
    if ctx.invoked_subcommand is None:
        await channel.send(
            'You can\'t use keyword on its own. Try `.keyword add bandos "bandos chestplate"` or `.keyword remove bandos` or `.keyword setname bandos "Bandos stuff"`')


def validate_quoted_item_name(name):
    pattern = re.compile('"([^"]*)"')

    match = pattern.match(name)

    return match and match.group() == name


@keyword.command(pass_context=True)
async def remove(ctx, keyword: str, *, name: str):
    user_id = ctx.message.author.id

    valid_name = validate_quoted_item_name(name)

    channel = ctx.channel

    if not valid_name:
        await channel.send('You didn\'t use this right. example: `.keyword remove bullshit`')
        return

    name = name.replace('"', '')

    success = ge.remove_keyword(user_id, keyword)

    if success:
        await channel.send('removed "{name}" from {keyword}'.format(keyword=keyword,
                                                               name=name))
    else:
        await channel.send('"{name}" not found or keyword {keyword} doesn\'t exist'.format(keyword=keyword,
                                                                                      name=name))


@keyword.command(pass_context=True)
async def delete(ctx, keyword: str):
    user_id = ctx.message.author.id

    success = ge.remove_keyword(user_id, keyword)

    channel = ctx.message.channel

    if success:
        await channel.send('Successfully removed keyword {keyword}'.format(keyword=keyword))
    else:
        await channel.send('Could not remove unknown keyword {keyword}'.format(keyword=keyword))


@keyword.command(pass_context=True)
async def setname(ctx, keyword: str, *, name: str):
    user_id = ctx.message.author.id

    valid_name = validate_quoted_item_name(name)

    channel = ctx.channel

    if not valid_name:
        await channel.send('You didn\'t use this right. example: `.keyword setname bullshit "bandos stuff"`')
        return

    name = name.replace('"', '')

    success = ge.set_name_for_keyword(user_id, keyword, name)

    if success:
        await channel.send('keyword group {keyword} is now named "{name}"'.format(keyword=keyword,
                                                                             name=name))
    else:
        await channel.send('keyword {keyword} not found'.format(keyword=keyword))


@keyword.command(pass_context=True)
async def add(ctx, keyword: str, *, item: str):
    user_id = ctx.message.author.id
    pattern = re.compile('"(\s|[a-z]|[A-Z]|\)|\(|\d|\'){3,}"')

    match = pattern.match(item)

    channel = ctx.channel

    if not match or match.group() != item:
        await channel.send('You didn\'t use this right. example: `.keyword add bullshit "bandos godsword"`')
        return

    item = item.replace('"', '')

    success, items = ge.set_keyword_for_item(user_id, keyword, item)

    if not success:
        await channel.send('unable to find "{item}"'.format(item=item))
        return

    items_str = ", ".join(items)

    await channel.send('{keyword} now contains '.format(keyword=keyword) + items_str)


@bot.command(pass_context=True)
async def update_messages(ctx):
    await ctx.channel.send("Starting message update")

    message_troller = MessageTroller()
    messages = await ctx.channel.history(limit=None).flatten()

    message_troller.store_messages(messages)
    await ctx.channel.send("Finished updating messages")

async def chris_command(ctx, query):
    await ctx.channel.trigger_typing()

    message_troller = MessageTroller()

    message = message_troller.random_chris_message(query)

    if message is None:
        await ctx.channel.send("Unable to find a message :(")
        return

    embed = discord.Embed(
        description="**[" + message.content + "](" + message.url + ")**",
        color=0xFF5733
    )
    embed.set_author(
        name="Chris",
        icon_url = chris_icon_url
    )

    date = datetime.fromtimestamp(message.date)
    date_string = date.strftime("%B %-d, %Y")
    embed.set_footer(text=date_string)

    await ctx.channel.send(embed=embed)

@bot.group(pass_context=True)
async def chris(ctx):
    if ctx.invoked_subcommand is None:
        await chris_command(ctx, None)

@bot.group(pass_context=True)
async def Chris(ctx):
    if ctx.invoked_subcommand is None:
        await chris_command(ctx, None)

@Chris.command(pass_context=True)
async def search(ctx, query: str):
    await chris_command(ctx, query)

@chris.command(pass_context=True)
async def search(ctx, query: str):
    await chris_command(ctx, query)

@bot.command(pass_context=True)
async def price(ctx, query: str):
    user_id = ctx.message.author.id
    group_name, results = ge.items(user_id, query)

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

    await ctx.channel.send(embed=embed)

bot.run(token)
