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
def updateMySqlData(guildid):
	with open("data.json", "r") as jsonFile:
		data = json.load(jsonFile)

	#storing everything but the password
	data["mysql"][guildid] = {entry:config.custom_mysql[guildid][entry] for entry in config.custom_mysql[guildid] if not entry == "password"}

	with open("data.json", "w") as jsonFile:
		json.dump(data, jsonFile)

#returns the MySQL connection using the credentials
def getMySqlConnection(guildid):
	for field in ["host", "username", "password", "database"]:
		if not field in config.mysql(guildid) or config.mysql(guildid)[field] == None:
			raise Exception(field + " not set")
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
		err = ""
		guildid = str(ctx.message.guild.id)
		command = arg[0]
		if len(arg) == 5:

			if command == 'setup':

				try:
					await ctx.message.delete()
				except:
					err = "I need the permission to delete messages."

				if not guildid in config.custom_mysql:
					config.custom_mysql[guildid] = config.default_mysql

				config.custom_mysql[guildid]["host"] = arg[1]
				config.custom_mysql[guildid]["database"] = arg[2]
				config.custom_mysql[guildid]["username"] = arg[3]
				config.custom_mysql[guildid]["password"] = arg[4]

				updateMySqlData(guildid)

				res = "MySQL setup successful."

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
					res = "Remote MySQL connection failed. Check the `"+config._prefixes(guildid)[0]+"mysql info` command."

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
					updateMySqlData(guildid)
					res = "Host set"
				elif arg[1] == 'database':
					config.custom_mysql[guildid]["database"] = arg[2]
					updateMySqlData(guildid)
					res = "Database name set"
				elif arg[1] == 'username':
					config.custom_mysql[guildid]["username"] = arg[2]
					updateMySqlData(guildid)
					res = "Username set"
				elif arg[1] == 'password':

					try:
						await ctx.message.delete()
					except:
						err = "I need the permission to delete messages."

					config.custom_mysql[guildid]["password"] = arg[2]
					updateMySqlData(guildid)
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
					res = "Remote MySQL connection failed. Check the `"+config._prefixes(guildid)[0]+"mysql info` command."

			#the info command to show the remote MySQL credentials
			#
			#ex: !mysql info
			elif command == 'info':
				res = "```ini\n[Host]	 " + (config.mysql(guildid)["host"] or "Not Set") + "\n" 
				res += "[Database] " + (config.mysql(guildid)["database"] or "Not Set") + "\n" 
				res += "[Username] " + (config.mysql(guildid)["username"]  or "Not Set")+ "\n"
				res += "[Password] " + ("[Set]" if "password" in config.mysql(guildid) and config.mysql(guildid)["password"] != None else "[Not Set]") + "\n```"

		if err != "":
			res = "`"+err+"`\n" + res

		await ctx.send(res)

def setup(client):
	client.add_cog(MySQL(client))