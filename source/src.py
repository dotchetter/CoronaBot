#!/usr/bin/python3

import os
import discord
import asyncio
import logging
from datetime import datetime, time
from dotenv import load_dotenv
from schedule import Schedule, Event, Weekday
from robbot import Brain
from custom_errs import EnvironmentVariableError
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
        CHANNEL = os.getenv('CHANNEL')
        LOGFORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
    except Exception as e:
        raise EnvironmentVariableError(f'Unable to load enviromnent variable: {e}')
    
    logging.basicConfig(
        level = logging.INFO, 
        filename = 'bot.log', 
        format = LOGFORMAT
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loop.create_task(self.auto_message())
        self.loop.create_task(self.purge_runtime())
        self.brain = Brain(name = 'Rob', schedule_url = RobBotClient.SCHDURL, hourdelta = 2)
        self.add_events()

    def add_events(self):
        '''
        Save pre-defined reoccuring messages / events in the Schedule instance.
        '''
        next_lesson = lambda: self.brain.next_lesson_response

        daily = Event(
            weekdays = [Weekday.TUESDAY, Weekday.WEDNESDAY, Weekday.FRIDAY], 
            time = time(hour = 8, minute = 0, second = 0), 
            body = next_lesson()
        )

        friday = Event(
            weekdays = [Weekday.FRIDAY], 
            time = time(hour = 15, minute = 30, second = 0),
            body = 'Wohoo, fredag! :beers: '
        )            
        
        self.brain.schedule.schedule_events(daily, friday)

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
        body = message.content.lower()
        messageUser = message.author.id
    
        if 'hej rob' in body and message.author != client.user:
            response = self.brain.respond_to(body,messageUser=messageUser)
            await message.channel.send(response)
            logging.info(f'{message.author} said {message.content}')
            logging.info(f'bot said {response}')
    
    async def auto_message(self):
        '''
        Loop indefinitely and send messages that are pre-
        defined on a certain day and a certain time.
        '''
        await client.wait_until_ready()
        channel = self.get_channel(RobBotClient.CHANNEL)
        
        while not self.is_closed():
            await asyncio.sleep(1)
            
            now = time(
                hour = self.brain.schedule.current_time.hour, 
                minute = self.brain.schedule.current_time.minute,
                second = self.brain.schedule.current_time.second
            )
            
            for event in self.brain.schedule.scheduled_events:
                for weekday in event.weekdays:
                    if weekday == self.brain.schedule.weekday and now == event.time:
                        await channel.send(event.body)
                        logging.info(f'BOT SAID: {event.body}')


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
            midnight = datetime(now.year, now.month, now.day,0, 0, 0)
            time_left = (midnight - now)

            await asyncio.sleep(time_left.seconds)
            logging.INFO('Commencing nightly purge and cleanup...')
            
            try:
                self.brain.schedule.set_calendar()
                self.brain.schedule.truncate_event_name()
                self.brain.schedule.adjust_event_hours(hourdelta = 2)
                removed_activities = self.brain.schedule.remove_activities()
            except Exception as e:
                logging.ERROR(f'Error occured while cleaning up: {e}')
            else:
                logging.info('Nightly purge and cleanup completed.')
            
            await asyncio.sleep(1)            
            if len(removed_activities):
                logging.info(f"Purged activities: {removed_activities}")

if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_TOKEN')
    client = RobBotClient()
    client.run(TOKEN)