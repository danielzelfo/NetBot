import os
import sys
import json

#change cwd to directory of file
os.chdir(os.path.dirname(os.path.realpath(__file__)))

optional_cogs = []

#the default data
default_prefixes = ['!']
default_mysql = {
    "host": None,
    "database": None,
    "username": None,
    "password": None
}

#custom user data
custom_mysql = {}
custom_prefixes = {}

#getting custom user data from json file
with open('data.json') as f:
    data = json.load(f)
custom_prefixes = data["prefixes"]
custom_mysql = data["mysql"]

#function to determine the bot command prefixes
async def prefixes(bot, message):
    return custom_prefixes.get(str(message.guild.id)) or default_prefixes

#obtain prefixes data using the guildid
def _prefixes(guildid):
    return custom_prefixes.get(guildid) or default_prefixes
#obtain mysql data using the guildid
def mysql(guildid):
    return custom_mysql.get(guildid) or default_mysql