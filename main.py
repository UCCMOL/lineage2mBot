# bot.py
import os
import dbm
import re
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
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
    print(message.content)
    db['save_word'] = message.content
    await message.channel.send(str(db['save_word'], "utf-8"))
    db.close()
    
client.run(TOKEN)