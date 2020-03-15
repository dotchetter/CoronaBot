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


client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i kina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i kina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i kina'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i sydkorea'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i sydkorea'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i sydkorea'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i italien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i italien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i italien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i iran'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i iran'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i iran'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i diamond princess'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i diamond princess'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i diamond princess'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i tyskland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i tyskland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i tyskland'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i frankrike'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i frankrike'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i frankrike'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i japan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i japan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i japan'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i spanien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i spanien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i spanien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i usa'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i usa'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i usa'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i singapore'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i singapore'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i singapore'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i england'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i england'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i england'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i schweitz'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i schweitz'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i schweitz'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i hong kong'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i hong kong'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i hong kong'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i sverige'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i sverige'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i sverige'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i norge'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i norge'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i norge'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i nederländerna'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i nederländerna'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i nederländerna'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i kuwait'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i kuwait'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i kuwait'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i bahrain'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i bahrain'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i bahrain'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i malaysia'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i malaysia'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i malaysia'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i australien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i australien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i australien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i belgien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i belgien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i belgien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i thailand'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i thailand'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i thailand'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i taiwan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i taiwan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i taiwan'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i österrike'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i österrike'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i österrike'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i canada'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i canada'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i canada'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i irak'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i irak'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i irak'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i island'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i island'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i island'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i grekland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i grekland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i grekland'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i indien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i indien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i indien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i uae'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i uae'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i uae'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i san marino'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i san marino'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i san marino'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i danmark'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i danmark'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i danmark'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i algeriet'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i algeriet'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i algeriet'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i israel'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i israel'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i israel'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i libanon'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i libanon'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i libanon'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i oman'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i oman'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i oman'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i vietnam'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i vietnam'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i vietnam'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i ecuador'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i ecuador'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i ecuador'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i tjeckien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i tjeckien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i tjeckien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i finland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i finland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i finland'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i macao'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i macao'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i macao'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i kroatien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i kroatien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i kroatien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i portugal'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i portugal'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i portugal'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i quatar'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i quatar'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i quatar'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i palestina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i palestina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i palestina'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i azerbaijan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i azerbaijan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i azerbaijan'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i belarus'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i belarus'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i belarus'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i irland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i irland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i irland'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i mexico'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i mexico'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i mexico'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i rumänien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i rumänien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i rumänien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i pakistan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i pakistan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i pakistan'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i saudi arabien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i saudi arabien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i saudi arabien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i brasilien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i brasilien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i brasilien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i georgien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i georgien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i georgien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i ryssland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i ryssland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i ryssland'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i senegal'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i senegal'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i senegal'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i filippinerna'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i filippinerna'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i filippinerna'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i egypten'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i egypten'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i egypten'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i estonia'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i estonia'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i estonia'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i nya zeeland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i nya zeeland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i nya zeeland'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i chile'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i chile'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i chile'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i slovenien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i slovenien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i slovenien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i indonesien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i indonesien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i indonesien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i marocko'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i marocko'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i marocko'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i bosnien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i bosnien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i bosnien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i ungern'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i ungern'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i ungern'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i afghanistan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i afghanistan'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i afghanistan'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i andorra'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i andorra'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i andorra'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i armenien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i armenien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i armenien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i cambodia'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i cambodia'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i cambodia'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i dominikanska republiken'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i dominikanska republiken'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i dominikanska republiken'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i jordanien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i jordanien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i jordanien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i lettland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i lettland'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i lettland'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i litauen'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i litauen'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i litauen'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i luxembourg'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i luxembourg'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i luxembourg'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i nordmakedonien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i nordmakedonien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i nordmakedonien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i monaco'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i monaco'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i monaco'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i nepal'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i nepal'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i nepal'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i nigeria'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i nigeria'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i nigeria'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i sri lanka'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i sri lanka'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i sri lanka'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i tunisien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i tunisien'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i tunisien'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i ukraina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i ukraina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i ukraina'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i argentina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i argentina'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i argentina'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i liechtenstein'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i liechtenstein'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i liechtenstein'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i polen'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i polen'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i polen'.split(' ')))

client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har smittats i sydafrika'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har omkommit i sydafrika'.split(' ')))
client.scheduler.every(1).minutes.do(
    pollcache, func = corona_ft.get_cases_by_country, 
    message = message_mock('hur många har tillfrisknat i sydafrika'.split(' ')))


# --- Turn the key and start the bot ---
client.run(environment_vars['DISCORD_TOKEN'])