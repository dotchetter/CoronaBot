import os
import json
import asyncio
import schedule
import discord

from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from pathlib import Path
from source.custom_errs import *
from source.event import Event
from source.weekdays import Weekdays

from source.features.LunchMenuFeature import LunchMenuFeature
from source.features.RedditJokeFeature import RedditJokeFeature
from source.features.ScheduleFeature import ScheduleFeature
from source.features.CoronaSpreadFeature import CoronaSpreadFeature
from source.commandintegrator.logger import logger
from source.commandintegrator import CommandProcessor, PronounLookupTable

'''
Details:
    2020-03-10 Simon Olofsson

Module details:
    Service main executable

Synposis:
    Initialize the bot with api reference to Discords
    services. Instantiate bot intelligence from separate
    modules. 
'''


class RobBotClient(discord.Client):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.loop.create_task(self.run_scheduler(self.automessage_channel)) # 
        self._guild = kwargs['DISCORD_GUILD']
        self._scheduler = schedule.Scheduler()
                        
    @property
    def scheduler(self):
        return self._scheduler

    @property
    def automessage_channel(self):
        return self._automessage_channel

    @automessage_channel.setter
    def automessage_channel(self, val: int):
        self._automessage_channel = val    

    @logger
    async def on_ready(self) -> None:
        '''
        This method is called as soon as the bot is online.
        '''
        for guild_name in client.guilds:
            if guild_name == self._guild:
                break
    @logger
    async def on_member_join(self, member: discord.Member) -> None:
        '''
        If a new member just joined our server, greet them warmly!
        '''
        greeting_phrase = self.brain.greet(member.name)
        await member.create_dm()
        await member.dm_channel.send(greeting_phrase)
    
    @logger    
    async def on_message(self, message: discord.Message) -> None: 
        '''
        Respond to a message in the channel if someone
        calls on the bot by name, asking for commands.
        '''
        now = datetime.now().strftime('%Y-%m-%d -- %H:%M:%S')    
        if message.content.lower().startswith('rob') and message.author != client.user:
            response = processor.process(message).response()
            await message.channel.send(response)

    @logger            
    async def run_scheduler(self, channel: int) -> None:
        '''
        Loop indefinitely and send messages that are pre-
        defined on a certain day and a certain time. 
        '''

        await client.wait_until_ready()
        channel = self.get_channel(channel) # Private. Edit on server.
        
        while not self.is_closed():            
            result = self.scheduler.run_pending(passthrough = True)
            if result: 
                for _, value in result.items():
                    if not value: 
                        continue
                    else: 
                        await channel.send(value)
            await asyncio.sleep(0.1)
   

def load_environment(env_var_strings: list) -> dict:
    """
    Return a dictionary comprehended with values for
    environment variables used to authenticate various
    interfaces throughout the bot application, loaded
    from an .env file by the use of load_dotenv().

    :param env_var_strings: 
        list with all keys to populate with value, the 
        same as in the ones in the .env file
    """
    load_dotenv()
    var_dict = {}

    for var in env_var_strings:
        var_dict[var] = os.getenv(var)

    return var_dict

if __name__ == '__main__':

    enviromnent_strings = [
        'DISCORD_GUILD',
        'TIMEEDIT_URL',
        'LUNCH_MENU_URL',
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT',
        'GOOGLE_API_KEY',
        'GOOGLE_CSE_ID',
        'DISCORD_TOKEN',
        'CORONA_API_URI',
        'CORONA_API_RAPIDAPI_HOST',
        'CORONA_API_RAPIDAPI_KEY'
    ]

    commandintegrator_settings_file = 'C:\\users\\admin\\git\\robbottherobot\\source\\commandintegrator\\commandintegrator.settings.json'
    corona_translation_file = 'C:\\users\\admin\\git\\robbottherobot\\source\\country_eng_swe_translations.json'

    with open(commandintegrator_settings_file, 'r', encoding = 'utf-8') as f:
        default_responses = json.loads(f.read())['default_responses']

    environment_vars = load_environment(enviromnent_strings)
    
    processor = CommandProcessor(
        pronoun_lookup_table = PronounLookupTable(), 
        default_responses = default_responses)
    

    #  --- Instantiate the feature objects used and the discord client object ---

    lunchmenu_ft = LunchMenuFeature(url = environment_vars['LUNCH_MENU_URL'])
    schedule_ft = ScheduleFeature(url = environment_vars['TIMEEDIT_URL'])
    corona_ft = CoronaSpreadFeature(
                    CORONA_API_URI = environment_vars['CORONA_API_URI'],
                    CORONA_API_RAPIDAPI_HOST = environment_vars['CORONA_API_RAPIDAPI_HOST'],
                    CORONA_API_RAPIDAPI_KEY = environment_vars['CORONA_API_RAPIDAPI_KEY'],
                    translation_file_path = corona_translation_file)

    redditjoke_ft = RedditJokeFeature(
                        client_id = environment_vars['REDDIT_CLIENT_ID'], 
                        client_secret = environment_vars['REDDIT_CLIENT_SECRET'],
                        user_agent = environment_vars['REDDIT_USER_AGENT'])
    
    processor.features = (lunchmenu_ft, lunchmenu_ft, corona_ft, redditjoke_ft)
    environment_vars['automessage_channel'] = 651080743388446750
    client = RobBotClient(**environment_vars)
    
    

    """
    Add scheduled methods here. If your method needs parameters, 
    simply add them after the name of the method. here's an example:
    
    <<< client.scheduler.every(1).minute.do(add_integers, a = 10, b = 5) >>>
    """


    client.scheduler.every().day.at('08:00').do(schedule_ft.get_todays_lessons)
    #client.scheduler.every().friday.at()

    # --- Turn the key and start the bot ---

    client.run(environment_vars['DISCORD_TOKEN'])