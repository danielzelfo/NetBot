import discord
from discord.ext import commands

import os
import sys
import json

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config

#update json file with data
def updatePrefixesData():
    with open("data.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["prefixes"] = config.custom_prefixes

    with open("data.json", "w") as jsonFile:
        json.dump(data, jsonFile)

#the Settings cog class
class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
	
	#the prefix command
    @commands.command()
    async def prefix(self, ctx, *arg):
        res = "Invalid command"
        guildid = str(ctx.message.guild.id)
        command = arg[0]
        if len(arg) == 2:
            #the add command to add a command prefix
            #
            #ex: !prefix add .
            if command == 'add':
                if not arg[1] in config._prefixes(guildid):
                    if not guildid in config.custom_prefixes:
                        config.custom_prefixes[guildid] = config.default_prefixes

                    config.custom_prefixes[guildid].append(arg[1])
                    updatePrefixesData()
                    res = "Command prefix added"
                else:
                    res = "Command prefix already exists"

            #the remove command to remove a command prefix
            #
            #ex: !prefix remove .  
            elif command == 'remove':
                
                if len(config._prefixes(guildid)) > 1:
                    if not guildid in config.custom_prefixes:
                        config.custom_prefixes[guildid] = config.default_prefixes

                    try:
                        config.custom_prefixes[guildid].remove(arg[1])
                        updatePrefixesData()
                        res = "Command prefix removed"
                    except:
                        res = "No such command prefix"
                else:
                    res = "You need at least one command prefix"
        
        #the list command to list all the command prefixes
        #
        #ex: !prefix list
        if len(arg) == 1:
            if command == 'list':
                res = "```ini\n["+"] [".join(config._prefixes(guildid))+"]\n```"
        await ctx.send(res)

def setup(client):
    client.add_cog(Settings(client))