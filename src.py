import os
import discord
import asyncio
import logging
from datetime import datetime, time
from dotenv import load_dotenv
from schedule import Schedule
from robbot import Brain

'''
Details:
    2019-09-25

Module details:
    Service main executable

Synposis:
    Initialize the bot with api reference to Discords
    services. Instantiate bot intelligence from separate
    modules. 
'''

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SCHDURL = os.getenv('TIMEEDIT_URL')

class RobBotCLient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loop.create_task(self.auto_message())
        self.loop.create_task(self.refresh_schedule())
        self.brain = Brain(name = 'Rob', schedule_url = SCHDURL, hourdelta = 2)
        log_format = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
        logging.basicConfig(level = logging.INFO, filename = 'bot.log', format = log_format)

    async def on_ready(self):
        '''
        This method is called as soon as the bot is online.
        '''
        for guild_name in client.guilds:
            if guild_name == GUILD:
                break
        logging.info(f'Bot is online at {guild_name}')

    async def on_member_join(self, member):
        '''
        If a new member just joined our server, greet them warmly!
        '''
        greeting_phrase = self.brain.greet(member.name)
    
        await member.create_dm()
        await member.dm_channel.send(greeting_phrase)
        logging.info(f'Bot said {greeting_phrase}')
    
    async def on_message(self, message):
        '''
        Respond to a message in the channel if someone
        calls on the bot by name, asking for commands.
        '''
        now = datetime.now().strftime('%Y-%m-%d -- %H:%M:%S')
        body = message.content.lower()
    
        if 'hej rob' in body and message.author != client.user:
            response = self.brain.respond_to(body)
            await message.channel.send(response)
            logging.info(f'{message.author} said {message.content}')
            logging.info(f'bot said {response}')
    
    async def auto_message(self):
        '''
        Loop indefinitely and send messages that are pre-
        defined on a certain day and / or a certain time.
        '''
        await client.wait_until_ready()
        channel = self.get_channel(628469370292535336)
        automatic_messages = {
            'friday': {
                'message': 'WOHOOOOOOOOOOO! Dags för fredagsölen! :beers:',
                'scheduled_time': time(15, 30)
            },
            'morning_next_lesson': {
                'message': self.brain.next_lesson_response,
                'scheduled_time': time(8, 0)
            }
        }
        
        while not self.is_closed():
            await asyncio.sleep(35)
            message = None
            now = self.brain.schedule.current_time
            now_time = time(now.hour, now.minute)
            
            if self.brain.schedule.weekday == 'friday':
                if now_time == automatic_messages['friday']['scheduled_time']:
                    message = automatic_messages['friday']['message']
            
            if now_time == automatic_messages['morning_next_lesson']['scheduled_time']:
                message = automatic_messages['morning_next_lesson']['message']

            if message:
                await channel.send(message)
                logging.info(f'--BOT SAID: {message}')


    async def refresh_schedule(self):
        '''
        Refresh the Schedule object with a new updated
        variant of the schedule from the web by using
        its own method for this. Perform this action
        daily at midnight.
        '''
        await client.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(1440)
            if self.brain.schedule.current_time.hour == 0:
                self.brain.schedule.set_calendar()
                self.brain.schedule.truncate_event_name()
                self.brain.schedule.adjust_event_hours(hourdelta = 2)
                logging.info(f'Refreshed calendar object')

if __name__ == '__main__':
    client = RobBotCLient()
    client.run(TOKEN)