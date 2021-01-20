# bot.py
import os
import dbm
import regex as re
import requests
import discord
import json
from replit import db
import time
import random
import datetime
from discord.ext import tasks
from datetime import timedelta
from dotenv import load_dotenv
from collections import OrderedDict 
from operator import getitem 
import keep_alive
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
SETTING_CHANNEL_ID = os.getenv('DISCORD_SETTING_CHANNEL_ID')
LOD_CHANNEL_ID=os.getenv('DISCORD_LOG_CHANNEL_ID')
UTC_PLUS  = 9
#regex = r"([\.!])([\w\p{Hangul}]+)\s*([\w\p{Hangul}]+)?\s*([\w\p{Hangul} \.]+)?"
regex = r"([\.!])([\w\p{Hangul}]+)\s*([\w\p{Hangul}]+)?\s*([\w\p{Hangul}\.]+)? *([\+])? *([\w\p{Hangul} \.]+)?"
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

client = discord.Client()
print(vars(client.http))
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
"릴리" : "블랙릴리",
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
                                            'new_time' : '<new_time>',
                                            'unborn_times' : '',
                                            'hide' :'',   # 1 = hide ,0 = not hide
                            
                                      }
                
                        }

'''
async def get_current_time():
    now = datetime.datetime.now(datetime.timezone.utc)
    return_time = now + timedelta(hours=UTC_PLUS)
    return_time = return_time.replace(tzinfo=None)
    return_time = datetime.datetime.strptime(return_time.strftime("%H%M"),"%H%M")
    return return_time

@tasks.loop(minutes=60.0)
async def show_boss_message_every_ten_minutes():
  channel = client.get_channel(int(LOD_CHANNEL_ID))
  boss_data = db['lineageBossTimer']
  if(boss_data):
      configs = json.loads(boss_data)
  else:
      configs = {"boss" : {}}
  await show_boss_messages(configs,channel)
  
@tasks.loop(minutes=1.0)
async def check_boss_time():
    channel = client.get_channel(int(CHANNEL_ID))
    boss_data = db['lineageBossTimer']
    if(boss_data):
        configs = json.loads(boss_data)
    else:
        configs = {"boss" : {}}
    now = await get_current_time()
    print("do event every minutes start",now)
    for key,value in configs["boss"].items():
        boss_last_time = datetime.datetime.strptime(configs["boss"][key]["last_time"],"%H%M")
        boss_next_time = datetime.datetime.strptime(configs["boss"][key]["new_time"],"%H%M")
        if(configs["boss"][key]["hide"]==1):
          continue
        boss_next_time_5_min_before = boss_next_time - timedelta(minutes=5)
        boss_next_time_4_min_before = boss_next_time - timedelta(minutes=4)
        boss_next_time_1_min_before = boss_next_time - timedelta(minutes=1)
        boss_next_time_30_min_after = boss_next_time + timedelta(minutes=30)
        if boss_next_time_5_min_before == now:
            response = "```\n"
            #히실로메 - 격전의 평원에서 5분 안에 리젠 됩니다! 예상 젠 시간 : 19:38
            response = response + str(key) + " " + str(value["place"]) + "에서 " + str(5) + "분 안에 리젠 됩니다! 예상 젠시간 :" + str(boss_next_time.strftime("%H:%M")) + "\n"
            response = response + "```"
            await channel.send(response,tts=True)
            print(5,key)
        if boss_next_time_1_min_before == now:
            response = "```\n"
            #히실로메 - 격전의 평원에서 1분 안에 리젠 됩니다! 예상 젠 시간 : 19:38
            response = response + str(key) + " " + str(value["place"]) + "에서 " + str(1) + "분 안에 리젠 됩니다! 예상 젠시간 :" + str(boss_next_time.strftime("%H:%M")) + "\n"
            response = response + "```"
            await channel.send(response,tts=True)
            print(1,key)
        if str(boss_next_time_30_min_after.strftime("%H%M")) == str(now.strftime("%H%M")):
            await boss_unreborn(configs,channel,key)
    db['lineageBossTimer'] = json.dumps(configs, default=myconverter)
    print("do event every minutes end")
@check_boss_time.before_loop
@show_boss_message_every_ten_minutes.before_loop
async def before_printer():
    print('waiting...')
    await client.wait_until_ready()



@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.id != GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    check_boss_time.start()
    show_boss_message_every_ten_minutes.start()
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if(str(message.channel.id) != str(CHANNEL_ID) and str(message.channel.id) != str(SETTING_CHANNEL_ID)):
        return
    boss_data = db['lineageBossTimer']
    commands = message.content;
    if(boss_data):
        configs = json.loads(boss_data)
    else:
        configs = {"boss" : {}}
    matches = re.finditer(regex, commands, re.MULTILINE)
    await do_commands(matches,configs,message.channel)
    db['lineageBossTimer'] = json.dumps(configs, default=myconverter)
    
async def show_boss_messages(configs,channel,boss_name = None):
    response = "```\n"
    if boss_name != None:
        if boss_name in nickname:
            boss_name = nickname[boss_name]
        if boss_name in configs["boss"]:
            boss_last_time = datetime.datetime.strptime(configs["boss"][boss_name]["last_time"],"%H%M")
            boss_next_time = boss_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
            response = response + str(boss_last_time.strftime("%H:%M")) + " -> " + str(boss_next_time.strftime("%H:%M")) + " " + str(boss_name) + " " + str(configs["boss"][boss_name]["place"]) + " 리센시간" + str(configs["boss"][boss_name]["reborn_time"]) + " "
            if configs["boss"][boss_name]["unborn_times"] > 0:
                response = response + "멍:" + str(configs["boss"][boss_name]["unborn_times"]) + "회 "
            response = response + str(configs["boss"][boss_name]["messages"]) + "\n"
    else:
        res = sorted(configs["boss"].items(), key = lambda x: x[1]['new_time']) 
        now = await get_current_time()
        now_time_in_int = int(now.strftime("%H%M"))
        for key,value in res:
            boss_new_time = datetime.datetime.strptime(configs["boss"][key]["new_time"],"%H%M")
            boss_new_time_in_int = int(boss_new_time.strftime("%H%M"))
            if(configs["boss"][key]["hide"]==1):
              continue
            if(boss_new_time_in_int > now_time_in_int and boss_new_time_in_int < 2400):
              boss_last_time = datetime.datetime.strptime(configs["boss"][key]["last_time"],"%H%M")
              boss_next_time = boss_last_time + timedelta(hours=float(configs["boss"][key]["reborn_time"]))
              response = response + str(boss_last_time.strftime("%H:%M")) + " -> " + str(boss_next_time.strftime("%H:%M")) + " " + str(key) + " " + " " + str(configs["boss"][key]["place"]) + " "
              if configs["boss"][key]["unborn_times"] > 0:
                  response = response + "멍:" + str(configs["boss"][key]["unborn_times"]) + "회 "
              response = response + str(value["messages"]) + "\n"
        for key,value in res:
            boss_new_time = datetime.datetime.strptime(configs["boss"][key]["new_time"],"%H%M")
            boss_new_time_in_int = int(boss_new_time.strftime("%H%M"))
            if(configs["boss"][key]["hide"]==1):
              continue
            if(boss_new_time_in_int <= now_time_in_int):
              boss_last_time = datetime.datetime.strptime(configs["boss"][key]["last_time"],"%H%M")
              boss_next_time = boss_last_time + timedelta(hours=float(configs["boss"][key]["reborn_time"]))
              response = response + str(boss_last_time.strftime("%H:%M")) + " -> " + str(boss_next_time.strftime("%H:%M")) + " " + str(key) + " " + " " + str(configs["boss"][key]["place"]) + " "
              if configs["boss"][key]["unborn_times"] > 0:
                  response = response + "멍:" + str(configs["boss"][key]["unborn_times"]) + "회 "
              response = response + str(value["messages"]) + "\n"
    response = response + "```"
    await channel.send(response)
async def update_boss_messages(configs,channel,boss_name = None,target = None , new_setting = None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        if target == "리젠시간":
            configs["boss"][boss_name]["reborn_time"] = float(new_setting)
            boss_last_time = datetime.datetime.strptime(configs["boss"][boss_name]["last_time"],"%H%M")
            boss_new_time = boss_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
            configs["boss"][boss_name]["new_time"] = boss_new_time.strftime("%H%M")
        elif target == "지역":
            configs["boss"][boss_name]["place"] = str(new_setting)
        await show_boss_messages(configs,channel,boss_name)
async def boss_unreborn(configs,channel,boss_name = None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        boss_last_time = datetime.datetime.strptime(configs["boss"][boss_name]["last_time"],"%H%M")
        boss_last_time = boss_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
        boss_new_time = boss_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
        configs["boss"][boss_name]["last_time"] = boss_last_time.strftime("%H%M")
        configs["boss"][boss_name]["new_time"] = boss_new_time.strftime("%H%M")
        configs["boss"][boss_name]["unborn_times"] = configs["boss"][boss_name]["unborn_times"] + 1
        await show_boss_messages(configs,channel,boss_name) 
async def create_boss_messages(configs,channel,boss_name = None,reborn_time = None,place = None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name not in configs["boss"]:
        now = await get_current_time()
        if place is None:
            place = ""
        new_time = now + timedelta(hours=float(reborn_time))
        configs["boss"][boss_name] = {"last_time": now.strftime("%H%M") , "reborn_time" : float(reborn_time) , "messages" : " " ,"place" : str(place) , "unborn_times" : 0 ,"new_time": new_time.strftime("%H%M"),"hide": 0}
        await show_boss_messages(configs,channel,boss_name)
async def hide_boss(configs,channel,boss_name= None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        configs["boss"][boss_name]["hide"]=1
        response = "```\n"
        response = response + str(boss_name) + " 숨김을 됐습니다\n"
        response = response + "```"
        await channel.send(response) 
async def delete_boss_messages(configs,channel,boss_name = None):
    if boss_name is None:
        return
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        configs["boss"].pop(boss_name, None)
        response = "```\n"
        response = response + str(boss_name) + " 삭제가 됐습니다\n"
        response = response + "```"
        await channel.send(response)
async def randompick(configs,channel,pick_num = 0,peoples = ""):
    people_array = peoples.split(' ')
    outcome = random.sample(people_array,k=int(pick_num))
    response = "```\n뽑기 결과\n"
    response = response + str(outcome)
    response = response + "```\n"
    await channel.send(response)
async def get_time_if_can(kill_time):
    if re.match(r"[0-9][0-9][0-9][0-9]?",kill_time):
        return True
    else:
        return False
async def kill_boss_messages(configs,channel,boss_name,kill_time = None , messages = None):
    if boss_name in nickname:
        boss_name = nickname[boss_name]
    if boss_name in configs["boss"]:
        configs["boss"][boss_name]["unborn_times"] = 0
        configs["boss"][boss_name]["hide"] = 0
        if messages != None:
            configs["boss"][boss_name]["messages"] = messages
        if kill_time != None:
            if re.match(r"[0-9][0-9][0-9][0-9]?",kill_time):    
                new_last_time = datetime.datetime.strptime(kill_time,"%H%M")
                boss_new_time = new_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
                configs["boss"][boss_name]["last_time"] = new_last_time.strftime("%H%M")
                configs["boss"][boss_name]["new_time"] = boss_new_time.strftime("%H%M")
        else:
            new_last_time = await get_current_time()
            boss_new_time = new_last_time + timedelta(hours=float(configs["boss"][boss_name]["reborn_time"]))
            configs["boss"][boss_name]["last_time"] = new_last_time.strftime("%H%M")
            configs["boss"][boss_name]["new_time"] = boss_new_time.strftime("%H%M")
        

        await show_boss_messages(configs,channel,boss_name) 
async def do_commands(matches,configs,channel):
    print(matches)
    for matchNum, match in enumerate(matches, start=1):
        print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
        if len(match.groups()) > 1:
            if match.group(1) == ".":
                if match.group(2) == "보스":
                    await show_boss_messages(configs,channel,match.group(3))
                elif match.group(2) == "컷":
                    await kill_boss_messages(configs,channel,match.group(3),kill_time = match.group(4),messages = match.group(6))
                elif match.group(2) == "멍":
                    await boss_unreborn(configs,channel,match.group(3))
                elif match.group(2) == "뽑기":
                    await randompick(configs,channel,pick_num = match.group(3),peoples = match.group(6))
                elif match.group(2) == "숨김":
                    await hide_boss(configs,channel,match.group(3))
            elif match.group(1) == "!":
                if match.group(2) == "설정":
                    await update_boss_messages(configs,channel,boss_name = match.group(3),target = match.group(4), new_setting = match.group(6))
                elif match.group(2) == "추가":
                    await create_boss_messages(configs,channel,boss_name = match.group(3),reborn_time = match.group(4),place = match.group(6))
                elif match.group(2) == "삭제":
                    await delete_boss_messages(configs,channel,boss_name = match.group(3))

keep_alive.keep_alive()
client.run(TOKEN)