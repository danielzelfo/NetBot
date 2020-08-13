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
default_ftp = {
    "host": None,
    "username": None,
    "password": None,
    "port": 21
}

#custom user data
custom_mysql = {}
custom_ftp = {}
custom_prefixes = {}

#getting custom user data from json file
with open('data.json') as f:
    data = json.load(f)
custom_prefixes = data["prefixes"]
custom_mysql = data["mysql"]
custom_ftp = data["ftp"]

#function to determine the bot command prefixes
async def prefixes(bot, message):
    return custom_prefixes.get(str(message.guild.id)) or default_prefixes

#obtain prefixes data using the guildid
def _prefixes(guildid):
    return custom_prefixes.get(guildid) or default_prefixes
#obtain mysql data using the guildid
def mysql(guildid):
    return custom_mysql.get(guildid) or default_mysql
#obtain ftp data using the guildid
def ftp(guildid):
    return custom_ftp.get(guildid) or default_ftp