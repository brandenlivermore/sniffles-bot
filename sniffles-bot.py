import discord
from pprint import pprint
from discord.ext import commands
from grand_exchange import GrandExchange, human_format
import sys

dev_environment = 'dev'
prod_environment = 'prod'

environment = None

def set_environment():
	if sys.argc is not 2:
		sys.exit('run this script with either -dev or -prod')
	
	if sys.argv[1] is '-dev':
		environment = dev_environment
	elif sys.argv[1] is '-prod':
		environment = prod_environment
	
	if environment is None:
		sys.exit('you didn\'t specify -dev or -prod')
		
	if environment is prod_environment:
		token = 'NDE4Njc4NjU4MTkwODAyOTQ0.DXlEow.Tm9Ru4-GKH2-X1rkA9p__8uZ8ls'
	elif environment is dev_environment:
		token = 'NDE5Nzc3MDA3NjU2NjMyMzIw.DX-8GQ.GHoW5mMaIGLkWGXyQgJ637Hq99c'



set_environment()

bot = commands.Bot(command_prefix='.', description='BigBoyBot D: :P')
ge = GrandExchange()


@bot.event
async def on_ready():
	await bot.change_presence(game=discord.Game(name='cat'))


@bot.command()
async def price(*, query: str):
	results = ge.items(query)
	
	text = ''
	
	for result in results:
		text += '{name}: {price}, today\'s change: {change}, alch price: {alch_price}\n'.format(name=result.name, price=human_format(result.price), change=human_format(result.change), alch_price=human_format(result.alch_price))
	
	if not results:
		text = 'nothing found for that shit'
	
	await bot.say(text)



bot.run(token))
