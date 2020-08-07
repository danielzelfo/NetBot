import os
import sys
import json

#change cwd to directory of file
os.chdir(os.path.dirname(os.path.realpath(__file__)))

optional_cogs = []

#the default data
default_prefixes = ['!']

#custom user data
custom_prefixes = {}

#getting custom user data from json file
with open('data.json') as f:
    data = json.load(f)
custom_prefixes = data["prefixes"]

#function to determine the bot command prefixes
async def prefixes(bot, message):
    return custom_prefixes.get(str(message.guild.id)) or default_prefixes

#obtain prefixes data using the guildid
def _prefixes(guildid):
    return custom_prefixes.get(guildid) or default_prefixes