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
[mysql]
	mysql set
		mysql set host <your_host>: sets host
		mysql set database <your_database>: sets database
		mysql set username <your_username>: sets username
		mysql set password <your_password>: sets password
	mysql test: tests remote MySQL connection
	mysql show <table> <column>: shows the content of the given column in the given table
	```"""
	await ctx.send(res)

bot.run('***bot_token***')