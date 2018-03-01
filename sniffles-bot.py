import discord
from pprint import pprint
from discord.ext import commands
import grand_exchange

client = commands.Bot(command_prefix='!', description='BigBoyBot D: :P')
ge = grand_exchange.GrandExchange()

@client.event
async def on_ready():
	await bot_client.change_presence(game=discord.Game(name='cat'))

@client.event
async def on_member_update(before, after):
	await bot_client.send_message(channel, message) 
	
@client.command()
async def price(query: str):
	results = ge.items(query)
	await bot_client.say(results[0].name)

# @client.event
# async def on_member_join(member):
# 	print('member join')





client.run('NDE4Njc4NjU4MTkwODAyOTQ0.DXlEow.Tm9Ru4-GKH2-X1rkA9p__8uZ8ls')
