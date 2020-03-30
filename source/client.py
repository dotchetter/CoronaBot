import os
import json
import asyncio
import discord
from schedule import Scheduler

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from pathlib import Path
from custom_errs import *
from weekdays import Weekdays

from features.CoronaSpreadFeature import CoronaSpreadFeature
from CommandIntegrator.logger import logger
from CommandIntegrator import CommandProcessor, PronounLookupTable, PollCache

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
class CoronaBotClient(discord.Client):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.loop.create_task(self.run_scheduler(self.automessage_channel))
        self._guild = kwargs['DISCORD_GUILD']
        self._scheduler = Scheduler()
                        
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

    async def run_scheduler(self, channel: int) -> None:
        """
        Loop indefinitely and send messages that are pre-
        defined on a certain day and a certain time. 
        """
        await client.wait_until_ready()
        channel = self.get_channel(channel)
        length_limit = 2000

        while not self.is_closed():            
            output = []
            combined = str()
            
            result = self.scheduler.run_pending(passthrough = True)
            if not result or datetime.now().hour >= 22 or datetime.now().hour < 8:
                await asyncio.sleep(0.1)
                continue
            
            while True:
                for _, message in result.items():
                    if message:
                        if len(combined) + len(message) >= 2000:
                            output.append(combined)
                            combined = str()
                        combined += f'{os.linesep}{message}'
                await asyncio.sleep(0.5)
                result = self.scheduler.run_pending(passthrough = True)
                if not result:
                    break

            if combined and not output:
                output.append(combined)
            
            [await channel.send(i) for i in output]
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

    CommandIntegrator_settings_file = Path('CommandIntegrator') / 'commandintegrator.settings.json'
    corona_translation_file = 'country_eng_swe_translations.json'

    with open(CommandIntegrator_settings_file, 'r', encoding = 'utf-8') as f:
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
    environment_vars['automessage_channel'] = 0 # Insert text channel ID here for auto messages 
    client = CoronaBotClient(**environment_vars)
    pollcache = PollCache(silent_first_call = True)
    

    """
    Add scheduled methods here. If your method needs parameters, 
    simply add them after the name of the method. here's an example:
    
    <<< client.scheduler.every(1).minute.do(add_integers, a = 10, b = 5) >>>
    """

    @dataclass
    class message_mock:
        content: list

    client.scheduler.every().day.at('21:30').do(corona_ft.get_total_deaths)
    client.scheduler.every().day.at('21:30').do(corona_ft.get_total_recoveries)
    client.scheduler.every().day.at('21:30').do(corona_ft.get_total_infections)

    with open(corona_translation_file, 'r', encoding = 'utf-8') as f:
        for country in json.loads(f.read())['swe_to_eng'].keys():
            client.scheduler.every(1).minutes.do(
                pollcache, func = corona_ft.get_cases_by_country, 
                message = message_mock(f'{country}'.split(' ')))

            client.scheduler.every(1).minutes.do(
                pollcache, func = corona_ft.get_deaths_by_country, 

                message = message_mock(f'{country}'.split(' ')))
            client.scheduler.every(1).minutes.do(
                pollcache, func = corona_ft.get_recoveries_by_country, 
                message = message_mock(f'{country}'.split(' ')))


    # --- Turn the key and start the bot ---
client.run(environment_vars['DISCORD_TOKEN'])