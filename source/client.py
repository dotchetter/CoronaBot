import os
import json
import discord
import asyncio
import logging
from datetime import datetime, time, timedelta
from source.commandintegrator.framework import CommandProcessor, PronounLookupTable
from dotenv import load_dotenv
from pathlib import Path
from source.custom_errs import *
from source.event import Event
from source.weekdays import Weekdays
from source.features.ReminderFeature import ReminderFeature
from source.features.LunchMenuFeature import LunchMenuFeature
from source.features.RedditJokeFeature import RedditJokeFeature
from source.features.ScheduleFeature import ScheduleFeature
#from source.schedule import Schedule
#from source.brain import Brain
#from source.reminder import Reminder

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

class RobBotClient(discord.Client):
    
    LOGFORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
    LOG_DIR = Path('runtime_logs')
    LOG_FILE = 'runtime.log'
    LOG_FILE_FULLPATH = LOG_DIR / LOG_FILE
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.loop.create_task(self.auto_message())
        #self.loop.create_task(self.purge_runtime())        
        self._guild = kwargs['DISCORD_GUILD']
        self.processor = commandprocessor= (ScheduleFeature(url = kwargs['TIMEEDIT_URL']),
                                  LunchMenuFeature(url = kwargs['LUNCH_MENU_URL']),
                                  RedditJokeFeature(client_id = kwargs['REDDIT_CLIENT_ID'], 
                                                    client_secret = kwargs['REDDIT_CLIENT_SECRET'],
                                                    user_agent = kwargs['REDDIT_USER_AGENT']))

        # if not os.path.isdir(self.brain.LOG_DIR):
        #     os.mkdir(self.brain.LOG_DIR)

        # logging.basicConfig(
        #     level = logging.INFO, 
        #     filename = RobBotClient.LOG_FILE_FULLPATH, 
        #     format = RobBotClient.LOGFORMAT)

    async def on_ready(self):
        '''
        This method is called as soon as the bot is online.
        '''
        for guild_name in client.guilds:
            if guild_name == self._guild:
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
    
        if message.content.lower().startswith('rob') and message.author != client.user:
            await message.channel.send(processor.process(message).response())
            try:
                logging.info(f'{message.author} said: {message.content}')
            except Exception:
                pass
            else:
                logging.info(f'Bot said: {response}')
    
    async def auto_message(self):
        '''
        Loop indefinitely and send messages that are pre-
        defined on a certain day and a certain time. 
        '''
        await client.wait_until_ready()
        channel = self.get_channel(000000000000000000) # Private. Edit on server.
        
        while not self.is_closed():
            await asyncio.sleep(1)
            event = self.brain.reminder.get()
            if event:
                await channel.send(event)
                try:
                    logging.info(f'Bot said: {event}')
                except Exception as e:
                    logging.error(f'Message could not log correctly. Error:\n {e}')
                
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
            midnight = datetime(now.year, now.month, now.day, 0, 10, 0)
            time_left = (midnight - now)

            await asyncio.sleep(time_left.seconds)
            logging.info('Commencing nightly purge and cleanup...')
            
            try:
                self.brain.schedule.set_calendar()
                self.brain.schedule.truncate_event_name()
                self.brain.schedule.adjust_event_hours(hourdelta = self._hourdelta)
                self.setup_reminders()
                removed_activities = self.brain.reminder.purge()
                self.brain.lunch_menu_scraper.purge_cache()

            except Exception:
                pass
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

def load_environment():
    
    load_dotenv()
    var_dict = {}
    env_var_strings = [
        'DISCORD_GUILD',
        'TIMEEDIT_URL',
        'LUNCH_MENU_URL',
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT',
        'GOOGLE_API_KEY',
        'GOOGLE_CSE_ID',
        'DISCORD_TOKEN'
    ]

    for var in env_var_strings:
        var_dict[var] = os.getenv(var)

    return var_dict

if __name__ == '__main__':
    
    commandintegrator_dir = Path('commandintegrator')
    response_file = 'commandprocessor.default.response.json'
    response_file_path = commandintegrator_dir / response_file

    with open(response_file_path, 'r', encoding = 'utf-8') as f:
        default_responses = json.loads(f.read())

    environment_vars = load_environment()
    processor = CommandProcessor(pronoun_lookup_table = PronounLookupTable(), 
                                default_responses = default_responses)
    
    processor.features = (ScheduleFeature(url = environment_vars['TIMEEDIT_URL']),
                          LunchMenuFeature(url = environment_vars['LUNCH_MENU_URL']),
                          RedditJokeFeature(client_id = environment_vars['REDDIT_CLIENT_ID'], 
                                            client_secret = environment_vars['REDDIT_CLIENT_SECRET'],
                                            user_agent = environment_vars['REDDIT_USER_AGENT']))


    friday = Event(body = 'Fredag, wohoo! :beers:',
                weekdays = [Weekdays.FRIDAY],
                time = time(hour = 16, minute = 0),
                alarm = timedelta(minutes = 30))
    
    client = RobBotClient(**environment_vars)
    #client.setup_reminders(reoccuring = [friday])
    client.run(environment_vars['DISCORD_TOKEN'])