# bot.py
import os
import dbm
import regex as re
import discord
import json
import time
import datetime
from discord.ext import tasks
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
#regex = r"([\.!])([\w\p{Hangul}]+)\s*([\w\p{Hangul}]+)?\s*([\w\p{Hangul} \.]+)?"
regex = r"([\.!])([\w\p{Hangul}]+)\s*([\w\p{Hangul}]+)?\s*([\w\p{Hangul}\.]+)? *?([\+])? *([\w\p{Hangul} \.]+)?"
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

client = discord.Client()
nickname = {
"트롬" : "트롬바",
"가" : "가레스",
"엔" : "엔쿠라",
"펜" : "오르펜",
"발" : "발보",
"티엘" : "티미니엘",
"셀" : "셀루",
"켈" : "켈소스",
"체" : "체르투바",
"바" : "바실라",
"개미" : "여왕개미",
"템" : "템페스트",
"펠" : "펠리스",
"사르" : "사르카",
"판드" : "판드라이드",
"돌크" : "돌연변이크루마",
"오크" : "오염된크루마",
"코어" : "코어수스캡터",
"판나" : "판나로드",
"마투" : "마투라",
"브" : "브래카",
"메" : "메두사",
"릴" : "블랙릴리",
"베" : "베히모스",
"드비" : "드래곤비스트",
"카" : "카탄",
"히실" : "히실로메",
"란" : "란도르",
"올" : "올크스",
"거울" : "망각의거울",
"사무" : "사무엘",
"글" : "글라키",
"우칸" : "우칸바",
"노르" : "노르무스",
"카브" : "카브리오",
"플린" : "플린트",
"안드" : "안드라스",
}
'''
configs => { 
                'boss' => {
                            '<boss_name>' => {
                                            'last_time': '<젠시간>',
                                            'reborn_time' : '<reborn time>',
                                            'messages' : '""',
                                            'place' : '<place>',
                            
                                      }
                
                        }

'''
@tasks.loop(minutes=1.0)
async def check_boss_time():
    channel = client.get_channel(int(CHANNEL_ID))
    print(channel)
    await channel.send("test")
@check_boss_time.before_loop
async def before_printer():
    print('waiting...')
    await client.wait_until_ready()



@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    check_boss_time.start()
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(message.channel.id)
    if(str(message.channel.id) != str(CHANNEL_ID)):
        return
    db = dbm.open('lineageBossTimer','c')
    commands = message.content;
    if "lineage2m" in db:
        configs = json.loads(str(db["lineage2m"],"utf-8"))
    else:
        configs = {"boss" : {}}
    matches = re.finditer(regex, commands, re.MULTILINE)
    await do_commands(matches,configs,message)
    db['lineage2m'] = json.dumps(configs, default=myconverter)
    db.close()
    
async def show_boss_messages(configs,server,boss_name = None):
    response = "```\n"
    if boss_name != None:
        if boss_name in nickname:
            boss_name = nickname[boss_name]
        if boss_name in configs["boss"]:
            boss_last_time = datetime.datetime.strptime(configs["boss"][boss_name]["last_time"],"%H%M")
            boss_next_time = boss_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
            response = response + str(boss_last_time.strftime("%H:%M")) + " -> " + str(boss_next_time.strftime("%H:%M")) + " " + str(boss_name) + " " + str(configs["boss"][boss_name]["messages"]) + "\n"
    else:
        for key,value in configs["boss"].items():
            boss_last_time = datetime.datetime.strptime(configs["boss"][key]["last_time"],"%H%M")
            boss_next_time = boss_last_time + timedelta(hours=float(configs["boss"][key]["reborn_time"]))
            response = response + str(boss_last_time.strftime("%H:%M")) + " -> " + str(boss_next_time.strftime("%H:%M")) + " " + str(key) + " " + str(value["messages"]) + "\n"
    response = response + "```"
    await server.channel.send(response)
async def update_boss_messages(configs,server,boss_name = None,reborn_time = None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        configs["boss"][boss_name]["reborn_time"] = float(reborn_time)
        await show_boss_messages(configs,server,boss_name)
async def create_boss_messages(configs,server,boss_name = None,reborn_time = None,place = None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name not in configs["boss"]:
        now = datetime.datetime.now()
        if place is None:
            place = ""
        configs["boss"][boss_name] = {"last_time": now.strftime("%H%M") , "reborn_time" : float(reborn_time) , "messages" : " " ,"place" : str(place)}
        await show_boss_messages(configs,server,boss_name)
async def delete_boss_messages(configs,server,boss_name = None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        configs["boss"].pop(boss_name, None)
        response = "```\n"
        response = response + str(boss_name) + " 삭제가 됐습니다\n"
        response = response + "```"
        await server.channel.send(response)
async def get_time_if_can(kill_time):
    if re.match(r"[0-9][0-9][0-9][0-9]?",kill_time):
        return True
    else:
        return False
async def kill_boss_messages(configs,server,boss_name,kill_time = None , messages = None):
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        boss_last_time = datetime.datetime.strptime(configs["boss"][boss_name]["last_time"],"%H%M")
        boss_last_time = boss_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
        configs["boss"][boss_name]["last_time"] = boss_last_time.strftime("%H%M")
        if messages != None:
            configs["boss"][boss_name]["messages"] = messages
        if kill_time != None:
            if re.match(r"[0-9][0-9][0-9][0-9]?",kill_time):    
                new_last_time = datetime.datetime.strptime(kill_time,"%H%M")
                configs["boss"][boss_name]["last_time"] = new_last_time.strftime("%H%M")
        await show_boss_messages(configs,server,boss_name) 
async def do_commands(matches,configs,server):
    print(matches)
    for matchNum, match in enumerate(matches, start=1):
        print(len(match.groups()))
        print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
        if len(match.groups()) > 1:
            if match.group(1) == ".":
                if match.group(2) == "보스":
                    print("in show_boss")
                    await show_boss_messages(configs,server,match.group(3))
                elif match.group(2) == "컷":
                    await kill_boss_messages(configs,server,match.group(3),kill_time = match.group(4),messages = match.group(6))
            elif match.group(1) == "!":
                if match.group(2) == "설정":
                    await update_boss_messages(configs,server,boss_name = match.group(3),reborn_time = match.group(4))
                elif match.group(2) == "추가":
                    await create_boss_messages(configs,server,boss_name = match.group(3),reborn_time = match.group(4),place = match.group(6))
                elif match.group(2) == "삭제":
                    await delete_boss_messages(configs,server,boss_name = match.group(3))
client.run(TOKEN)