import discord
from discord.ext import commands

import os
import sys
import json

from ftplib import FTP

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config

#update json file with data
def updateFtpData():
    with open("data.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["ftp"] = config.custom_ftp

    with open("data.json", "w") as jsonFile:
        json.dump(data, jsonFile)

#check if ftp credentials are set
def ftpIsSet(guildid):
    return config.ftp(guildid)["host"] != None and config.ftp(guildid)["username"] != None and config.ftp(guildid)["password"] != None

#tries the FTP connection
def tryFtp(ftpobj):
    try:
        ftpobj.voidcmd("NOOP")
        return True
    except:
        return False

#get the ftp object
def getFtp(guildid):
    return FTP(config.ftp(guildid)["host"], config.ftp(guildid)["username"], config.ftp(guildid)["password"], config.ftp(guildid)["port"])

#ftp objects dictionary to hold ftp objects of all guilds
ftpobjs = {}

#the FTP cog class
class Ftp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
	
	#the ftp command
    @commands.command()
    async def ftp(self, ctx, *arg):
        command = arg[0]
        guildid = str(ctx.message.guild.id)
        res = "Invalid command"

        #copying default ftp setup for new user
        if not guildid in config.custom_ftp:
            config.custom_ftp[guildid] = config.default_ftp

        #setting the ftp object if necessary
        if not guildid in ftpobjs or not tryFtp(ftpobjs[guildid]):
            ftpobjs[guildid] = getFtp(guildid)

        if len(arg) == 5:
            #the setup command with the port
            #
            #ex: !ftp setup asd.wbsite.com myuser mypassword 2121
            if(command == 'setup'):
                
                config.custom_ftp[guildid]["host"] = arg[1]
                config.custom_ftp[guildid]["username"] = arg[2]
                config.custom_ftp[guildid]["password"] = arg[3]
                config.custom_ftp[guildid]["port"] = arg[4]

                
                ftpobjs[guildid] = getFtp(guildid)
                
                if( tryFtp(ftpobjs[guildid]) ):
                    updateFtpData()
                    res = "ftp setup successful"
                else:
                    config.custom_ftp[guildid] = config.default_ftp
                    res = "ftp setup failed"
        
        if len(arg) == 4:
            #the setup command
            #
            #ex: !ftp setup asd.wbsite.com myuser mypassword
            if(command == 'setup'):
                
                config.custom_ftp[guildid]["host"] = arg[1]
                config.custom_ftp[guildid]["username"] = arg[2]
                config.custom_ftp[guildid]["password"] = arg[3]
                
                ftpobjs[guildid] = getFtp(guildid)
                
                if( tryFtp(ftpobjs[guildid]) ):
                    updateFtpData()
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
                        try:
                            ftpobjs[guildid].cwd(arg[2])
                            res = "Current working directory set"
                        except:
                            res = "Invalid directory"
                    else:
                        res = "MySQL credentials not set"
            
        elif len(arg) == 2:
            #the get command to send a file to the chat
            #
            #ex: !ftp get index.php
            if command == 'get':
                if ftpIsSet(guildid):
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
                        res = "File does not exist"
                else:
                    res = "MySQL credentials not set"
        elif len(arg) == 1:

            #the list command will list all files and subdirectories in the current working directory
            #
            #ex: !ftp list
            if command == 'list':
                if ftpIsSet(guildid):
                        dirList = []
                        ftpobjs[guildid].retrlines('LIST', dirList.append)

                        for idx, item in enumerate(dirList):
                            s = item.split(' ')
                            dirList[idx] = " ".join(s[0:-1])+ " ["+s[-1]+"]"

                        res = "```ini\n"+"\n".join(dirList)+"\n```"
                else:
                    res = "MySQL credentials not set"
        
        if(res != ""):
            await ctx.send(res)

def setup(client):
    client.add_cog(Ftp(client))