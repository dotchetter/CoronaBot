import os
import discord
import random
from dotenv import load_dotenv

'''
College class chat bot for discord.

'''

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()

@client.event
async def on_ready():
    '''
    This method is called as soon as the bot is online.
    '''

    for guild_name in client.guilds:
        if guild_name == GUILD:
            break

    print(
        f'{client.user} says: Rusty bolts and fried circuits - I feel alive!',
        f'{client.user} is connected to {guild_name}',
        sep = '\n'
    )

@client.event
async def on_member_join(member):
    '''
    If a new member just joined our server, greet them 
    warmly!
    '''

    greeting_phrase = f'Bless my silicon! {member.name} - Welcome! Please nick your real name.'

    await member.create_dm()
    await member.dm_channel.send(
        f' Right click the server icon',
        f'and select Change Nickname.'
    )


@client.event
async def on_message(message):
    '''
    Respond to a message in the channel if someone
    calls on the bot by name, asking for commands.
    '''

    response_phrases = (
        'Ja?'
        'It\'s a me!',
        'Har inget bra svar på det..?',
        'Det sägs att det är mitt namn.',
        'Jag gillar att läsa mina loggar när jag laddar.',
        'Tacka min idiot till programmerare för denna tomma respons.',
        'Jag hoppas att göra bättre nytta en dag, men det är inte upp till mig!',
        'Inget slår en snabbladdning och en riktigt bra patch en fredagkväll, eller hur?',
    )

    if message.author != client.user:
        if 'hej rob' in message.content.lower():
            response = random.choice(response_phrases)
            await message.channel.send(response)
            # Debug
            print(
                f' - devlog: human said {message}',
                f' - devlog: bot said {response}',
                sep = '\n'
            )


client.run(TOKEN)