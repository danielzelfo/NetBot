import discord
from discord.ext import commands

import os
import sys
import json
import requests
import re

from ftplib import FTP

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config

bot = commands.Bot(command_prefix=config.prefixes)

#update json file with data
def updateFtpData(guildid):
	with open("data.json", "r") as jsonFile:
		data = json.load(jsonFile)

	#storing everything but the password
	data["ftp"][guildid] = {entry:config.custom_ftp[guildid][entry] for entry in config.custom_ftp[guildid] if not entry == "password"}

	with open("data.json", "w") as jsonFile:
		json.dump(data, jsonFile)

#check if ftp credentials are set
def ftpIsSet(guildid):
	for key in ["host", "username", "password"]:
		if not key in config.ftp(guildid):
			config.ftp(guildid)[key] = None
	return config.ftp(guildid)["host"] != None and config.ftp(guildid)["username"] != None and config.ftp(guildid)["password"] != None

#tries the FTP connection
def tryFtp(ftpobj):
	try:
		ftpobj.voidcmd("NOOP")
		return True
	except:
		return False

def validFtp(guildid):
	if guildid in ftpobjs:
		ftpgood = False
		if not tryFtp(ftpobjs[guildid]):
			#ftp test command failed - trying to reset the object
			try:
				ftpobjs[guildid] = getFtp(guildid)
				ftpgood = tryFtp(ftpobjs[guildid])
			except:
				pass
		else:
			ftpgood = True

		if ftpgood:
			return True
		return False
	return False

def credsNotSet(guildid):
	for key in ["host", "username", "password"]:
		if not key in config.ftp(guildid):
			config.ftp(guildid)[key] = None
	return [entry for entry in config.custom_ftp[guildid] if config.custom_ftp[guildid][entry] == None]

#get the ftp object
def getFtp(guildid):
	return FTP(config.ftp(guildid)["host"], config.ftp(guildid)["username"], config.ftp(guildid)["password"], config.ftp(guildid)["port"])

# Check if directory exists (in current location)
def directory_exists(ftpobj, dir):
	filelist = []
	ftpobj.retrlines('LIST',filelist.append)
	return any(f.split()[-1] == dir and f.upper().startswith('D') for f in filelist)

#ftp objects dictionary to hold ftp objects of all guilds
ftpobjs = {}

#the FTP cog class
class Ftp(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.MAXMSGLENGTH = 2000

	#the ftp command
	@commands.command()
	async def ftp(self, ctx, *arg):
		command = arg[0]
		guildid = str(ctx.message.guild.id)
		res = "Invalid command"
		err = ""

		#copying default ftp setup for new user
		if not guildid in config.custom_ftp:
			config.custom_ftp[guildid] = config.default_ftp

		#setting the ftp object if necessary
		if not guildid in ftpobjs:
			try:
				ftpobjs[guildid] = getFtp(guildid)
			except:
				pass

		if len(arg) == 5:
			#the setup command with the port
			#
			#ex: !ftp setup asd.wbsite.com myuser mypassword 2121
			if(command == 'setup'):

				try:
					await ctx.message.delete()
				except:
					err = "I need the permission to delete messages."

				config.custom_ftp[guildid]["host"] = arg[1]
				config.custom_ftp[guildid]["username"] = arg[2]
				config.custom_ftp[guildid]["password"] = arg[3]
				config.custom_ftp[guildid]["port"] = arg[4]

				ftpobjs[guildid] = getFtp(guildid)

				if tryFtp(ftpobjs[guildid]) :
					updateFtpData(guildid)
					res = "ftp setup successful"
				else:
					config.custom_ftp[guildid] = config.default_ftp
					res = "ftp setup failed"

		if len(arg) == 4:
			#the setup command
			#
			#ex: !ftp setup asd.wbsite.com myuser mypassword
			if(command == 'setup'):

				try:
					await ctx.message.delete()
				except:
					err = "I need the permission to delete messages."

				config.custom_ftp[guildid]["host"] = arg[1]
				config.custom_ftp[guildid]["username"] = arg[2]
				config.custom_ftp[guildid]["password"] = arg[3]

				ftpobjs[guildid] = getFtp(guildid)

				if tryFtp(ftpobjs[guildid]):
					updateFtpData(guildid)
					res = "ftp setup successful"
				else:
					config.custom_ftp[guildid] = config.default_ftp
					res = "ftp setup failed"

		elif len(arg) == 3:
			#the set commmand
			if command == 'set':
				#set the current working directory
				#
				#ex: !ftp set cwd htdocs
				if arg[1] == 'cwd':

					if ftpIsSet(guildid):
						if validFtp(guildid):
							try:
								ftpobjs[guildid].cwd(arg[2])
								res = "Current working directory set to `" + "`/`".join(arg[2].split("/")) + "`."
							except:
								res = "Invalid directory"
						else:
							res = "FTP credentials invalid."
					else:
						res = "FTP `"+"`,`".join(credsNotSet(guildid))+"` not set."

				elif arg[1] == 'host':
					config.custom_ftp[guildid]["host"] = arg[2]

					if ftpIsSet(guildid):
						ftpobjs[guildid] = getFtp(guildid)

						if tryFtp(ftpobjs[guildid]):
							res = "ftp host set.\nftp setup successful."
						else:
							res = "ftp host set.\ncurrent ftp credentials invalid."
					else:
						res = "ftp host set."

					updateFtpData(guildid)

				elif arg[1] == 'username':
					config.custom_ftp[guildid]["username"] = arg[2]

					if ftpIsSet(guildid):
						ftpobjs[guildid] = getFtp(guildid)

						if tryFtp(ftpobjs[guildid]):
							res = "ftp username set.\nftp setup successful."
						else:
							res = "ftp username set.\ncurrent ftp credentials invalid."
					else:
						res = "ftp username set."
					updateFtpData(guildid)

				elif arg[1] == 'password':
					try:
						await ctx.message.delete()
					except:
						err = "I need the permission to delete messages."

					config.custom_ftp[guildid]["password"] = arg[2]

					if ftpIsSet(guildid):
						ftpobjs[guildid] = getFtp(guildid)

						if tryFtp(ftpobjs[guildid]):
							res = "ftp password set.\nftp setup successful."
						else:
							res = "ftp password set.\ncurrent ftp credentials invalid."
					else:
						res = "ftp password set."
					updateFtpData(guildid)

				elif arg[1] == 'port':
					config.custom_ftp[guildid]["port"] = arg[2]

					if ftpIsSet(guildid):
						ftpobjs[guildid] = getFtp(guildid)

						if tryFtp(ftpobjs[guildid]) :
							res = "ftp port set.\nftp setup successful."
						else:
							res = "ftp port set.\ncurrent ftp credentials invalid."
					else:

						res = "ftp port set."

					updateFtpData(guildid)

		elif len(arg) == 2:
			#the get command to send a file to the chat
			#ex: !ftp get index.php
			if command == 'get':
				if ftpIsSet(guildid):
					if validFtp(guildid):
						try:
							#temporary directory for file to be downloaded
							try:
								os.mkdir("temp")
							except:
								pass

							os.chdir("temp")
							filename = arg[1]

							# getting the file
							localfile = open(filename, 'wb')
							ftpobjs[guildid].retrbinary('RETR ' + filename, localfile.write, 1024)
							localfile.close()

							#sendning the file
							await ctx.send(file=discord.File(filename))

							#deleting the file and temporary directory
							os.remove(filename)
							res = ""

							os.chdir("../")
							os.rmdir("temp")

						except:
							res = "File does not exist."
					else:
						res = "FTP credentials not valid."
				else:
					res = "FTP `"+"`,`".join(credsNotSet(guildid))+"` not set."
			elif command == 'drop':
				if not "drop" in config.custom_ftp[guildid]:
					config.custom_ftp[guildid]["drop"] = {}
				config.custom_ftp[guildid]["drop"][str(ctx.message.channel.id)] = arg[1]
				updateFtpData(guildid)
				res = "FTP drop event to directory `"+ "`/`".join(arg[1].split("/")) +"` added."

		elif len(arg) == 1:

			#the list command will list all files and subdirectories in the current working directory
			#
			#ex: !ftp list
			if command == 'list':
				if ftpIsSet(guildid):
					if validFtp(guildid):
						dirList = []
						ftpobjs[guildid].retrlines('LIST', dirList.append)

						for idx, item in enumerate(dirList):
							#finding time with regex (it is the last thing before the file name)
							res = re.search(r'([0-1]?[0-9]|2[0-3]):[0-5][0-9]', dirList[idx])
							#highlighting file name
							dirList[idx] = dirList[idx][:res.end()+1]+"["+dirList[idx][res.end()+1:]+"]"

						res = "```ini\n"+"\n".join(dirList)+"\n```"
					else:
						res = "FTP credentials not valid."
				else:
					res = "FTP `"+"`,`".join(credsNotSet(guildid))+"` not set."

			elif command == 'drop':
				if not "drop" in config.custom_ftp[guildid]:
					config.custom_ftp[guildid]["drop"] = {}
				config.custom_ftp[guildid]["drop"][str(ctx.message.channel.id)] = ""
				updateFtpData(guildid)
				res = "FTP drop event added."

			elif command == 'test':
				if ftpIsSet(guildid):
					if validFtp(guildid):
						res = "FTP credentials valid."
					else:
						res = "FTP credentials not valid."
				else:
					res = "FTP `"+"`,`".join(credsNotSet(guildid))+"` not set."

		if err != "":
			res = "`"+err+"`\n" + res

		if res != "":
			#checking if the message is above the maximum message length
			if len(res) <= self.MAXMSGLENGTH:
				await ctx.send(res)
			else:
				#potential markdown - splitting into different messages
				if "```" in res:
					resSplit = res.split("```")
					if len(resSplit) > 2:
						#splitting sections by code block markers
						#odd number of code block markers
						if len(resSplit) % 2 == 0:
							resTemp = resSplit[-2] + "```" + resSplit[-1]
							resSplit = resSplit[:-2]
							resSplit.append(resTemp)

						#re-adding code block markers
						for i in range(len(resSplit)):
							if i % 2 == 1:
								resSplit[i] = f"```{resSplit[i]}```"

						resSplit = [r for r in resSplit if not r == ""]
					else:
						#only one code block marker
						resSplit = ["```".join(resSplit)]
				else:
					resSplit = [res]

				for res in resSplit:
					if res.startswith("```") and res.endswith("```"):
						msgCodeLang = res[3:6]
						chunkLengths = self.MAXMSGLENGTH - 11
						res = res[7:-4]
						resList = [f"```{msgCodeLang}\n"+res[i:i+chunkLengths]+"\n```" for i in range(0, len(res), chunkLengths)]
					else:
						resList = [res[i:i+self.MAXMSGLENGTH] for i in range(0, len(res), self.MAXMSGLENGTH)]

					#sending the message in chunks
					for m in resList:
						await ctx.send(m)


	#listener for any message
	@commands.Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:

			guildid = str(message.guild.id)
			res = ""
			#checking if drop is configured
			if len(message.attachments) > 0 and "drop" in config.custom_ftp[guildid] and str(message.channel.id) in config.custom_ftp[guildid]["drop"]:

				if ftpIsSet(guildid):
					if validFtp(guildid):
						for attachment in message.attachments:

							#setting the ftp object if necessary
							if not guildid in ftpobjs or not tryFtp(ftpobjs[guildid]):
								ftpobjs[guildid] = getFtp(guildid)

							#going to the base directory in the ftp server
							org_dir = ftpobjs[guildid].pwd()
							ftpobjs[guildid].cwd("/")

							#temporary directory for file to be downloaded
							try:
								os.mkdir("temp")
							except:
								pass

							os.chdir("temp")

							#downloading file
							file_request = requests.get(attachment.url)
							with open(attachment.filename, 'wb') as f:
								f.write(file_request.content)

							#uploading file
							dir = config.custom_ftp[guildid]["drop"][str(message.channel.id)]
							if dir != "":
								#creating any directory if not exist
								for d in dir.split("/"):
									if not directory_exists(ftpobjs[guildid], d):
										ftpobjs[guildid].mkd(d)
									ftpobjs[guildid].cwd(d)
							with open(attachment.filename, 'rb') as file:
								ftpobjs[guildid].storbinary('STOR '+attachment.filename, file)

							url = "ftp://"+ os.path.join(config.ftp(guildid)["host"], dir, attachment.filename).replace("\\", "/")

							res = "File uploaded to `"+url+"`" 

							#back to original directory
							for i in range(len(dir.split("/"))):
								ftpobjs[guildid].cwd("../")

							#going back to the original directory in the ftp server
							ftpobjs[guildid].cwd(org_dir)

							os.remove(attachment.filename)

							os.chdir("../")
							os.rmdir("temp")
					else:
						res = "Invalid FTP credentials."
				else:
					res = "FTP `"+"`,`".join(credsNotSet(guildid))+"` not set."

			if not res =="":
				await message.channel.send(res)

def setup(client):
	client.add_cog(Ftp(client))