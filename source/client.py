import os
import json
import asyncio
import schedule
import discord

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from pathlib import Path
from custom_errs import *
from event import Event
from weekdays import Weekdays

from features.CoronaSpreadFeature import CoronaSpreadFeature
from commandintegrator.logger import logger
from commandintegrator import CommandProcessor, PronounLookupTable, PollCache

"""
Details:
    2020-03-10 Simon Olofsson

Module details:
    Service main executable

Synposis:
    Initialize the bot with api reference to Discords
    services. Instantiate bot intelligence from separate
    modules. 
"""

pollcache = PollCache(silent_first_call = True)
class RobBotClient(discord.Client):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.loop.create_task(self.run_scheduler(self.automessage_channel))
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
        """
        This method is called as soon as the bot is online.
        """
        for guild_name in client.guilds:
            if guild_name == self._guild:
                break
    @logger
    async def on_member_join(self, member: discord.Member) -> None:
        """
        If a new member just joined our server, greet them warmly!
        """
        with open('greeting.dat', 'r', encoding = 'utf-8') as f:
            greeting_phrase = f.read()
            await member.create_dm()
            await member.dm_channel.send(greeting_phrase)
    
    @logger    
    async def on_message(self, message: discord.Message) -> None: 
        """
        Respond to a message in the channel if someone
        calls on the bot by name, asking for commands.
        """
        now = datetime.now().strftime('%Y-%m-%d -- %H:%M:%S')    
        if message.content.lower().startswith('!') and message.author != client.user:
            response = processor.process(message).response()
            if response: await message.channel.send(response)

    @logger            
    async def run_scheduler(self, channel: int) -> None:
        """
        Loop indefinitely and send messages that are pre-
        defined on a certain day and a certain time. 
        """
        await client.wait_until_ready()
        channel = self.get_channel(channel)

        while not self.is_closed():
            result = self.scheduler.run_pending(passthrough = True)
            if result: 
                for _, value in result.items():
                    if value: await channel.send(value)
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
        'DISCORD_TOKEN',
        'CORONA_API_URI',
        'CORONA_API_RAPIDAPI_HOST',
        'CORONA_API_RAPIDAPI_KEY'
    ]

    commandintegrator_settings_file = '/home/pi/RobBotTheRobot/source/commandintegrator/commandintegrator.settings.json'
    corona_translation_file = '/home/pi/RobBotTheRobot/source/country_eng_swe_translations.json'

    with open(commandintegrator_settings_file, 'r', encoding = 'utf-8') as f:
        default_responses = json.loads(f.read())['default_responses']

    environment_vars = load_environment(enviromnent_strings)
    
    

    #  --- Instantiate the key backend objects used and the discord client ---

    corona_ft = CoronaSpreadFeature(
                    CORONA_API_URI = environment_vars['CORONA_API_URI'],
                    CORONA_API_RAPIDAPI_HOST = environment_vars['CORONA_API_RAPIDAPI_HOST'],
                    CORONA_API_RAPIDAPI_KEY = environment_vars['CORONA_API_RAPIDAPI_KEY'],
                    translation_file_path = corona_translation_file)

    processor = CommandProcessor(
        pronoun_lookup_table = PronounLookupTable(), 
        default_responses = default_responses)
    
    processor.features = (corona_ft,)
    
    environment_vars['automessage_channel'] = 687629900555091995
    client = RobBotClient(**environment_vars)
    

    """
    Add scheduled methods here. If your method needs parameters, 
    simply add them after the name of the method. here's an example:
    
    <<< client.scheduler.every(1).minute.do(add_integers, a = 10, b = 5) >>>
    """

@dataclass
class message_mock:
    content: list


pollcache = PollCache()

with open(corona_translation_file, 'r', encoding = 'utf-8') as f:
    for count, key in enumerate(json.loads(f.read())['swe_to_eng'].keys()):

        client.scheduler.every(1).minutes.do(
            pollcache, func = corona_ft.get_cases_by_country, message = message_mock(
                f'hur många har smittats i {key}'.split(' ')))

        client.scheduler.every(1).minutes.do(
            pollcache, func = corona_ft.get_cases_by_country, message = message_mock(
                f'hur många har omkommit i {key}'.split(' ')))

        client.scheduler.every(1).minutes.do(
            pollcache, func = corona_ft.get_cases_by_country, message = message_mock(
                f'hur många har tillfrisknat i {key}'.split(' ')))

    # --- Turn the key and start the bot ---
client.run(environment_vars['DISCORD_TOKEN'])