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
	mysql setup <host> <database> <username> <password>: sets the mysql server credentials
	mysql set
		mysql set host <host>: sets mysql host
		mysql set database <database>: sets mysql database
		mysql set username <username>: sets mysql username
		mysql set password <password>: sets mysql password
	mysql test: tests remote MySQL connection
	mysql show <table> <column>: shows the content of the given column in the given table
[ftp]
	ftp setup <host> <user> <password> <port (optional)>: sets the ftp server credentials
	ftp set
		ftp set host <host>: sets the ftp host
		ftp set username <username>: sets the ftp username
		ftp set password <password>: sets the ftp password
		ftp set port <port>: sets the ftp port
		ftp set cwd <directory>: sets the current working directory
	ftp get <file_name>: sends file to chat
	ftp drop <absolute_directory_path (optional)>: add event to upload files sent to current channel to the provided directory in the ftp server
	ftp list: lists all files and subdirectories in the current working directory
	ftp test: tests the ftp credentials
[net]
	link <linkname> <url>: creates a link to a url... send '>linkname' to see the url
	unlink <linkname>: removes a set link in the server
	showlinks: shows a list of the links in the server
	xray <url>: gets the url that a given link would redirect to
	```"""
	await ctx.send(res)

bot.run('***bot_token***')