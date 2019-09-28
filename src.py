import os
import discord
import random
import robbot
from dotenv import load_dotenv

'''
Details:
    2019-09-25

Module details:
    Application main executable; Discord bot intelligence

Synposis:
    Initialize the bot with api reference to Discords
    services. Instantiate bot intelligence from separate
    modules. 
'''

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CALURL = 'https://cloud.timeedit.net/nackademin/web/1/ri6555Qy1446n6QZ0YQ4Q7ZQZ5607.ics'

client = discord.Client()
schedule = robbot.Schedule(url = CALURL)

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
    await member.dm_channel.send(greeting_phrase)


@client.event
async def on_message(message):
    '''
    Respond to a message in the channel if someone
    calls on the bot by name, asking for commands.
    '''

    recursive_response = False
    body = message.content.lower()

    if message.author == client.user:
        recursive_response = True
    
    if 'hej rob' in body and not recursive_response:
        if 'klassrum' in body or 'när börjar' or 'nästa lektion' in body:
            classroom = schedule.next_lesson_classroom
            time = schedule.next_lesson_time
            date = schedule.next_lesson_date
            response = f'Nästa lektion är i {classroom}, {date} klockan {time} :smirk:'
            await message.channel.send(response)
        elif 'dagens schema' in body:
            if schedule.todays_lessons:
                lessons_string = str('\n').join(schedule.todays_lessons)
                response = f'Här är dagens schema:\n{lessons_string}'
            else:
                response = 'Det ser inte ut att finnas några fler lektioner på schemat idag.'
        else:
            response = 'Hmm, jag är inte säker på att jag fattade det där.'
            await message.channel.send(response)

        # Debug
        print(
            f' - devlog: human said {message.content}',
            f' - devlog: bot said {response}',
            sep = '\n'
        )

if __name__ == '__main__':
    client.run(TOKEN)