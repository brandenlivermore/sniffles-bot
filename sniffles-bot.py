import discord
from pprint import pprint
from discord.ext import commands
from grand_exchange import GrandExchange, human_format

bot = commands.Bot(command_prefix='.', description='BigBoyBot D: :P')
ge = GrandExchange()

@bot.event
async def on_ready():
	await bot.change_presence(game=discord.Game(name='cat'))
"""
@bot.event
async def on_member_update(before, after):
	await bot.send_message(channel, message) 
"""	
@bot.command()
async def price(query: str):
	results = ge.items(query)
	
	text = ''
	
	for result in results:
		text += '{name}: {price}, today\'s change: {change}, alch price: {alch_price}\n'.format(name=result.name, price=human_format(result.price), change=human_format(result.change), alch_price=human_format(result.alch_price))

	await bot.say(text)


bot.run('NDE4Njc4NjU4MTkwODAyOTQ0.DXlEow.Tm9Ru4-GKH2-X1rkA9p__8uZ8ls')
