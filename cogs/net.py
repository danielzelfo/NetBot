import discord
from discord.ext import commands
import requests

import os
import sys

import json

import re

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import config


#function to update links in remote mysql database
def updateLinks():
	with open("data.json", "r") as jsonFile:
		data = json.load(jsonFile)

	data["links"] = config.custom_links

	with open("data.json", "w") as jsonFile:
		json.dump(data, jsonFile)

#the Links cog class
class Net(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	#listening to all message events
	@commands.Cog.listener()
	async def on_message(self, message):

		if not message.author.bot:
			#checking if the link prefix is used
			if(len(message.content) > 0 and message.content[0] == '>'):
				#sending the url if a link name is sent
				command = message.content[1:].split()[0]
				if str(message.guild.id) in config.custom_links and command in config.custom_links[str(message.guild.id)]:
					await message.channel.send(config.custom_links[str(message.guild.id)][command])

	#the link command - creates a link to a url... send '>linkname' to see the url
	@commands.command()
	async def link(self, ctx, linkname, result):
		if not str(ctx.guild.id) in config.custom_links:
			config.custom_links[str(ctx.guild.id)] = {}

		if re.match("^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$", result):
			config.custom_links[str(ctx.guild.id)][linkname] = result
			await ctx.send("Added link.")
			updateLinks()
		else:
			await ctx.send("Invalid url.")

	#the link command - removes a set link in the guild
	@commands.command()
	async def unlink(self, ctx, linkname):
		if not str(ctx.guild.id) in config.custom_links:
			config.custom_links[str(ctx.guild.id)] = {}

		del config.custom_links[str(ctx.guild.id)][linkname]
		await ctx.send("Removed link.")
		updateLinks()

	#the showlinks command - shows a list of the links in the guild
	@commands.command()
	async def showlinks(self, ctx):
		if not str(ctx.guild.id) in config.custom_links:
			config.custom_links[str(ctx.guild.id)] = {}

		if len(config.custom_links[str(ctx.guild.id)]) > 0:
			await ctx.send(str(config.custom_links[str(ctx.guild.id)])[1:-1].replace(", ", "\n"))
		else:
			await ctx.send("No links.")

	#xray command - gets the url that a given link would redirect to
	@commands.command()
	async def xray(self, ctx, url):
		if re.match("^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$", url):
			await ctx.send(requests.get("https://unshorten.me/s/" + url).content.decode("utf-8"))
		else:
			await ctx.send("Invalid url.")

def setup(client):
	client.add_cog(Net(client))