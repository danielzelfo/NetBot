import discord
from discord.ext import commands

import os
import sys
import json

import pymysql.cursors
import re

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config

# getting from the database
def getFromDB(table, cursor):
    #selecting the url with the given guildid and link name
    sql = "SELECT * FROM `" + table + "`"
    cursor.execute(sql)
    return cursor.fetchone()

#update json file with data
def updateMySqlData():
    with open("data.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["mysql"] = config.custom_mysql

    with open("data.json", "w") as jsonFile:
        json.dump(data, jsonFile)

#returns the MySQL connection using the credentials
def getMySqlConnection(guildid):
    return pymysql.connect(host=config.mysql(guildid)["host"],
                           user=config.mysql(guildid)["username"],
                           password=config.mysql(guildid)["password"],
                           db=config.mysql(guildid)["database"],
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

#the MySQL cog class
class MySQL(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
	
	#the mysql command
    @commands.command()
    async def mysql(self, ctx, *arg):
        res = "Invalid command"
        guildid = str(ctx.message.guild.id)
        command = arg[0]

        if len(arg) == 3:
            #the show command to show the content of a column in a table
            #
            #ex: !mysql show my_table the_column
            if command == 'show':
                table = arg[1]
                column = arg[2]
                try:
                    #connection to remote mysql server
                    connection = getMySqlConnection(guildid)
                    try:
                        with connection.cursor() as cursor:
                            res = "```\n"+str(json.loads(getFromDB(arg[1], cursor)[column]))+"\n```"
                    except:
                        res = "Invalid table and/or column"
                    finally:
                        connection.close()
                except: 
                    res = "Remote MySQL connection failed."
            
            #the set command to set the remote MySQL credentials
            #
            '''
            ex: !mysql set host 123.111.231.11
                !mysql set database db_Name
                !mysql set username my_user
                !mysql set password secret123
            '''
            if command == 'set':
                if not guildid in config.custom_mysql:
                    config.custom_mysql[guildid] = config.default_mysql
                
                if arg[1] == 'host':
                    config.custom_mysql[guildid]["host"] = arg[2]
                    updateMySqlData()
                    res = "Host set"
                elif arg[1] == 'database':
                    config.custom_mysql[guildid]["database"] = arg[2]
                    updateMySqlData()
                    res = "Database name set"
                elif arg[1] == 'username':
                    config.custom_mysql[guildid]["username"] = arg[2]
                    updateMySqlData()
                    res = "Username set"
                elif arg[1] == 'password':
                    config.custom_mysql[guildid]["password"] = arg[2]
                    updateMySqlData()
                    res = "Password set"
            
        elif len(arg) == 1:
            #the test command to test the remote MySQL credentials
            #
            #ex: !mysql test
            if command == 'test':
                try:
                    #connection to remote mysql server
                    connection = getMySqlConnection(guildid)
                    res = "Connected successfully"
                    connection.close()
                except: 
                    res = "Connection failed"
            
            #the info command to show the remote MySQL credentials
            #
            #ex: !mysql info
            elif command == 'info':
                res = "```ini\n[Host]     " + (config.mysql(guildid)["host"] or "Not Set") + "\n" 
                res += "[Database] " + (config.mysql(guildid)["database"] or "Not Set") + "\n" 
                res += "[Username] " + (config.mysql(guildid)["username"]  or "Not Set")+ "\n"
                res += "[Password] " + (config.mysql(guildid)["password"] or "Not Set") + "\n```"
        
        await ctx.send(res)

def setup(client):
    client.add_cog(MySQL(client))