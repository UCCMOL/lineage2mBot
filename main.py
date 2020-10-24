# bot.py
import os
import dbm
import regex as re
import discord
import json
import time
import datetime
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
regex = r"([\.!])([\w\p{Hangul}]+)\s+([\w\p{Hangul}]+)?\s+([\w\p{Hangul} \.]+)?"
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

client = discord.Client()
'''
configs => { 
                'boss' => {
                            '<boss_name>' => {
                                            'last_time': '<젠시간>',
                                            'reborn_time' : '<reborn time>',
                                            'messages' : '""',
                            
                                      }
                
                        }

'''
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    db = dbm.open('lineageBossTimer','c')
    commands = message.content;
    if "lineage2m" in db:
        configs = json.loads(str(db["lineage2m"],"utf-8"))
    else:
        configs = {"boss" : {}}
    matches = re.finditer(regex, commands, re.MULTILINE)
    print("before do commandsd",configs)
    do_commands(matches,configs)
    print("after do commandsd",configs)
    db['lineage2m'] = json.dumps(configs, default=myconverter)
    db.close()
    
def show_boss_messages(configs):
    for key,value in configs["boss"].items():
        print(key,value["last_time"],value["reborn_time"],value["messages"])
def update_boss_messages(configs,boss_name,reborn_time):
    if boss_name in configs["boss"]:
        configs["boss"][boss_name]["reborn_time"] = reborn_time
def create_boss_messages(configs,boss_name,reborn_time):
    if boss_name not in configs["boss"]:
        now = datetime.datetime.now()
        configs["boss"][boss_name] = {"last_time": now.strftime("%H%M") , "reborn_time" : reborn_time , "messages" : ""}
def delete_boss_messages(configs,boss_name):
    if boss_name in configs["boss"]:
        configs["boss"].pop(boss_name, None)
def kill_boss_messages(configs,boss_name,messages = ""):
    if boss_name in configs["boss"]:
        boss_last_time = datetime.datetime.strptime(configs["boss"][boss_name]["last_time"],"%H%M")
        boss_last_time = boss_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
        configs["boss"][boss_name]["last_time"] = boss_last_time.strftime("%H%M")
        if messages != "" :
            configs["boss"][boss_name]["messages"] = messages
def do_commands(matches,configs):
    print("in do_commands")
    print(matches)
    print(configs)
    for matchNum, match in enumerate(matches, start=1):
        print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
        if len(match.groups()) > 1:
            if match.group(1) == ".":
                if match.group(2) == "보스":
                    show_boss_messages(configs)
                elif match.group(2) == "컷":
                    if len(match.groups()) == 3:
                        kill_boss_messages(configs,match.group(3))
                    elif len(match.groups()) >3:
                        kill_boss_messages(configs,match.group(3),match.group(4))
            elif match.group(1) == "!":
                if match.group(2) == "설정":
                    if len(match.groups()) > 3:
                        update_boss_messages(configs,match.group(3),match.group(4))
                elif match.group(2) == "추가":
                    if len(match.groups()) > 3:
                        create_boss_messages(configs,match.group(3),match.group(4))
                elif match.group(2) == "삭제":
                    if len(match.groups()) > 3:
                        delete_boss_messages(configs,match.group(3))
client.run(TOKEN)