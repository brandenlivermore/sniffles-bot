import discord
from pprint import pprint
from discord.ext import commands
import grand_exchange

bot = commands.Bot(command_prefix='.', description='BigBoyBot D: :P')
ge = grand_exchange.GrandExchange()

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
	await bot.say(results[0].name)


bot.run('NDE4Njc4NjU4MTkwODAyOTQ0.DXlEow.Tm9Ru4-GKH2-X1rkA9p__8uZ8ls')
