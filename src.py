import os
import discord
from dotenv import load_dotenv

'''
College class chat bot for discord.
'''

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
guild = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} Beep bop, hello world!')

client.run(token)