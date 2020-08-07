import discord
import os
from os import path

from discord.ext import commands

import config

bot = commands.Bot(command_prefix=config.prefixes)

#change cwd to directory of file
os.chdir(os.path.dirname(os.path.realpath(__file__)))


#loading all the cogs from the cogs folder that aren't optional
for filename in os.listdir('cogs'):
    if filename.endswith('.py') and not filename[:-3] in config.optional_cogs:
        bot.load_extension('cogs.'+filename[:-3])

@bot.event
async def on_ready():
    print('We have logged in as ' + str(bot.user))

bot.remove_command('help')
@bot.command()
async def help(ctx):
	res = """```ini
[help] shows this message
[prefix]
	prefix add <prefix>: adds a command prefix
	prefix remove <prefix>: removes a command prefix
	prefix list: lists all command prefixes
	```"""
	await ctx.send(res)

bot.run('***bot_token***')