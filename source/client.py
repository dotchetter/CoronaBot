import os
import discord
import asyncio
import logging
from custom_errs import *
from datetime import datetime, time, timedelta
from schedule import Schedule, Event, Weekdays
from dotenv import load_dotenv
from robbot import Brain
from reminder import Reminder
from pathlib import Path

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

class RobBotClient(discord.Client):
    
    try:
        GUILD = os.getenv('DISCORD_GUILD')
        SCHDURL = os.getenv('TIMEEDIT_URL')
        LOGFORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
    except Exception as e:
        raise EnvironmentVariableError(f'Unable to load enviromnent variable: {e}')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop.create_task(self.auto_message())
        self.loop.create_task(self.purge_runtime())
        self.brain = Brain(schedule_url = RobBotClient.SCHDURL, hourdelta = kwargs['hourdelta'])
    
        try:
            logfile = Path('runtime.log')
            logging.basicConfig(
                level = logging.INFO, 
                filename = self.brain.LOG_DIR / logfile, 
                format = RobBotClient.LOGFORMAT)
        except FileNotFoundError:
            if not os.path.isdir(self.brain.LOG_DIR):
                os.mkdir(self.brain.LOG_DIR)

    async def on_ready(self):
        '''
        This method is called as soon as the bot is online.
        '''
        for guild_name in client.guilds:
            if guild_name == RobBotClient.GUILD:
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
    
        if 'hej rob' in message.content.lower() and message.author != client.user:
            response = self.brain.respond_to(message)
            await message.channel.send(response)
            logging.info(f'{message.author} said: {message.content}')
            logging.info(f'Bot said: {response}')
    
    async def auto_message(self):
        '''
        Loop indefinitely and send messages that are pre-
        defined on a certain day and a certain time. 
        '''
        await client.wait_until_ready()
        channel = self.get_channel(618476154688634890)
        
        while not self.is_closed():
            await asyncio.sleep(1)
            event = self.brain.reminder.get()
            if event:
                message = f'**Påminnelse:**\r\n{event}'
                await channel.send(message)
                logging.info(f'Bot said: {message}')
                
    async def purge_runtime(self):
        '''
        Refresh the Schedule object with a new updated
        variant of the schedule from the web by using
        its own method for this. Perform this action
        daily at midnight.
        '''
        await client.wait_until_ready()
        while not self.is_closed():

            now = self.brain.schedule.current_time
            midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
            time_left = (midnight - now)

            await asyncio.sleep(time_left.seconds)
            logging.info('Commencing nightly purge and cleanup...')
            
            try:
                self.brain.schedule.set_calendar()
                self.brain.schedule.truncate_event_name()
                self.brain.schedule.adjust_event_hours(hourdelta = 2)
                self.setup_reminders()
                removed_activities = self.brain.reminder.purge()

            except Exception as e:
                logging.error(f'Error occured while cleaning up: {e}')
            else:
                logging.info('Nightly purge and cleanup completed.')
                await asyncio.sleep(1)            
                if len(removed_activities):
                    logging.info(f"Purged activities: {removed_activities}")

    def setup_reminders(self, reoccuring = []):
        '''
        Create Event instances and keep them in Reminders object
        for each day. If lessons or events are encountered for given 
        current day, these will be represented by an Event instance.
        '''

        if len(self.brain.schedule.todays_events):
            for element in self.brain.schedule.todays_events:
                self.brain.reminder.add(Event(
                    body = element.name, 
                    date = element.begin.date(),
                    time = element.begin.adjusted_time,
                    location = element.location,
                    curriculum_event = True,
                    alarm = timedelta(hours = 1)))

        if len(reoccuring):
            for element in reoccuring:
                self.brain.reminder.add_reoccuring(element)

        if self.brain.reminder.events:
            logging.info(f'Added reminders:\n{self.brain.reminder.events}')

if __name__ == '__main__':
    
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    friday = Event(body = 'Fredag, wohoo! :beers:',
                weekdays = [Weekdays.FRIDAY],
                time = time(hour = 16, minute = 0),
                alarm = timedelta(minutes = 30))
    
    client = RobBotClient(**{'hourdelta': 2})
    client.setup_reminders(reoccuring = [friday])
    client.brain.load_unrecognized_message_history()

    client.run(TOKEN)