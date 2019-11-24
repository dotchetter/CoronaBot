import os
import json
import praw
from custom_errs import *
from enum import Enum, auto
from datetime import datetime, time, timedelta
from schedule import Schedule
from event import Event
from reminder import Reminder
from random import choice, seed, randint
from operator import attrgetter
from dataclasses import dataclass
from pathlib import Path
from unrecognizedcommand import UnrecognizedCommand
from responseoptions import ResponseOptions
from websearch import Websearch

'''
Details:
    2019-09-25

Module details:
    Application backend logic; Discord bot intelligence

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class schedule and then
    share the current classroom for the day or week in the chat
    with a chatbot. 
'''

seed(datetime.now().timestamp())

class Brain:
    '''
    Chatbot intelligence. Different bot features
    will be represented by class methods. Functionalities
    vary from being able to understand questions, commanded
    phrases and such. A core functionality for this bot is
    the ability to subscribe to a .ics schedule link, and 
    provide the current classroom for given lesson when 
    asked.
    '''
    
    LOG_DIR = Path('runtime_logs')
    UNRECOGNIZED_CMDS_CACHE_FILE = 'unrecognized_commands.json'
    UNRECOGNIZED_CMDS_CACHE_FULLPATH = LOG_DIR / UNRECOGNIZED_CMDS_CACHE_FILE
    
    MISUNDERSTOOD_PHRASES = (
        'Haha!',
        'Mjaa det låter bra!',
        'Ja visst!',
        'Jag håller med.',
        'Säger du det?',
        'Menar du det?'
    )
    
    KEYWORDS = {
        'rum': ResponseOptions.NEXT_LESSON,
        'nästa lektion': ResponseOptions.NEXT_LESSON,
        'lektioner idag': ResponseOptions.TODAYS_LESSONS,
        'lektioner': ResponseOptions.TODAYS_LESSONS,
        'vad kan du': ResponseOptions.SHOW_BOT_COMMANDS,
        'schema': ResponseOptions.SCHEDULE,
        'kan du komma ihåg': ResponseOptions.REMEMBER_EVENT,
        'påminna': ResponseOptions.REMEMBER_EVENT,
        'tent': ResponseOptions.SHOW_EVENTS,
        'händelser': ResponseOptions.SHOW_EVENTS,
        'events': ResponseOptions.SHOW_EVENTS,
        'aktiviteter': ResponseOptions.SHOW_EVENTS,
        'skämt': ResponseOptions.JOKE,
        'rob är': ResponseOptions.ADJECTIVE,
        'du är': ResponseOptions.ADJECTIVE,
        'klockan': ResponseOptions.TIMENOW,
        '?': ResponseOptions.WEBSEARCH,
        'vad är': ResponseOptions.WEBSEARCH
    }

    DISCORD_MSG_LENGTH_LIMIT = 2000

    def __init__(self, *args, **kwargs):
        self._commands = self._get_bot_commands()
        self._unrecognized_commands = []
        
        self.reminder = Reminder()
        self.schedule = Schedule(kwargs['schedule_url'])
        self.schedule.adjust_event_hours(hourdelta = kwargs['hourdelta'])
        
        self.websearch = Websearch(developerKey = kwargs['google_api_key'],
                                customsearch_id = kwargs['google_cse_id'])
       
        self.reddit = praw.Reddit(client_id = kwargs['reddit_client_id'], 
                                client_secret = kwargs['reddit_client_secret'],
                                user_agent = kwargs['reddit_user_agent'])

    def respond_to(self, message):
        '''
        Call private interpretation method to get enum instance
        which points toward which response to give. 
        Unrecognized messages recieved by people are logged separately
        for further development purposes and easy data harvesting.
        '''

        interpretation = self._interpret(message = message.content)
        
        if not interpretation:
            self._log_unrecognized_message(message)
            return f'{choice(Brain.MISUNDERSTOOD_PHRASES)}'
        elif interpretation == ResponseOptions.NEXT_LESSON:
            response = self._get_next_lesson_response()
        elif interpretation == ResponseOptions.TODAYS_LESSONS:
            response = self._get_todays_lessons_phrase()
        elif interpretation == ResponseOptions.SCHEDULE:
            response = self._get_schedule_phrase()
        elif interpretation == ResponseOptions.SHOW_BOT_COMMANDS:
            response = self.commands
        elif interpretation == ResponseOptions.MEANING_OF_LIFE:
            response = '42'
        elif interpretation == ResponseOptions.REMEMBER_EVENT:
            response = self._remember_event(message)
        elif interpretation == ResponseOptions.SHOW_EVENTS:
            response = self._get_remembered_events()
        elif interpretation == ResponseOptions.JOKE:
            response = self._joke()
        elif interpretation == ResponseOptions.TIMENOW:
            response = self._get_timenow_response()
        elif interpretation == ResponseOptions.ADJECTIVE:
            response = self._get_adjective_response(message)
        elif interpretation == ResponseOptions.WEBSEARCH:
            response = self._get_websearch_response(message)

        return response

    def greet(self, member = str):
        '''
        Return a greeting string, introducing ourselves
        and welcoming the new member to the class.
        '''
        try:
            with open('greeting.dat', 'r', encoding = 'utf-8') as f:
                greeting = str().join(f.readlines())
                return f'{greeting} {member}! :smile:'
        except FileNotFoundError:
            return 'Ett fel uppstod - jag hittar inte filen. Hjälp!'

    def _log_unrecognized_message(self, message):
        '''
        Create UnrecognizedCommand instance representing
        the message which was not understood by the bot.
        Write to a local .json file as the list of instances
        grows larger during runtime.
        '''   
        entry = UnrecognizedCommand(
                command = str(message.content),
                author = str(message.author),
                timestamp = datetime.now())
        
        self._unrecognized_commands.append(entry.__dict__)

        try:
            if not os.path.isdir(Brain.LOG_DIR):
                os.mkdir(Brain.LOG_DIR)
            
            with open(Brain.UNRECOGNIZED_CMDS_CACHE_FULLPATH, 'w', 
                encoding = 'utf-8') as f:
                    json.dump(self._unrecognized_commands, f,
                        ensure_ascii = False, indent = 4)
        
        except Exception as e:
            raise UnrecognizedCommandLoggingError(e)

    def load_unrecognized_message_history(self):
        '''
        Upon bot launch, load previously cached non-recognized phrases
        in to self._unrecognized_commands field.
        '''
        try:
            if os.path.isfile(Brain.UNRECOGNIZED_CMDS_CACHE_FULLPATH):
                with open(Brain.UNRECOGNIZED_CMDS_CACHE_FULLPATH, 'r',
                    encoding = 'utf-8') as f:
                        self._unrecognized_commands = json.loads(f.read())
        except Exception as e:
            raise UnrecognizedCommandLoggingError(f'Could not load file. {e}')

    def _get_bot_commands(self):
        '''
        Return string that shows the human what this bot can do, 
        and how to formulate a question.
        '''
        try:
            with open('commands.dat', 'r', encoding = 'utf-8') as f:
                return str().join(f.readlines())
        except Exception as e:
            raise FileNotFoundError(f'Could not parse commands.dat file: {e}')

    def _get_todays_lessons_phrase(self):
        '''
        Return concatenated response phrase with all lessons for 
        the current date. If none, return a message that explains
        no lessons for current date.
        '''
        if self.schedule.todays_lessons:
            lessons = '\n'.join(self.schedule.todays_lessons)
            return f'Här är schemat för dagen:\n{lessons}'
        return 'Det finns inga lektioner på schemat idag :sunglasses:'

    def _get_schedule_phrase(self):
        '''
        Return string with the schedule for as long as forseeable
        with Schedule object. Take in to acount the 2000 character
        message limit in Discord. Append only until the length
        of the total string length of all elements combined are within
        0 - 2000 in length.s
        '''
        friendly_schedule = []
        last_date = self.schedule.curriculum[0].begin.date()
        allowed_length = Brain.DISCORD_MSG_LENGTH_LIMIT
        
        for index, event in enumerate(self.schedule.curriculum):
            if event.begin.date() >= self.schedule.today:
                begin = event.begin.adjusted_time.strftime('%H:%M')
                end = event.end.adjusted_time.strftime('%H:%M')
                location = event.location
                name = event.name
                date = event.begin.date()
                
                if date != last_date:
                    phrase = f'\n{name}\nKlassrum: {location}\nNär: {date} -- {begin}-{end}'
                else:
                    phrase = f'{name}\nKlassrum: {location}\nNär: {date} -- {begin}-{end}\n'
        
                if (allowed_length - len(phrase)) > 10:
                    friendly_schedule.append(phrase)
                    allowed_length -= len(phrase)
                    last_date = event.begin.date()
                else:
                    break        
        friendly_schedule = '\n'.join(friendly_schedule)        
        return f'**Här är schemat!** :slight_smile:\n\n{friendly_schedule}'


    def _get_next_lesson_response(self):
        '''
        Return string with concatenated variable values to tell the
        human which is the next upcoming lesson.
        '''
        date = self.schedule.next_lesson_date
        hour = self.schedule.next_lesson_time
        classroom = self.schedule.next_lesson_classroom
        schedule =  self.schedule.curriculum
        todays_lessons = self.schedule.todays_lessons
        return f'Nästa lektion är i {classroom}, {date}, kl {hour} :slight_smile:'

    def _remember_event(self, message):
        '''
        If the bot recieves a message with proper syntax, create
        an Event instance. Save this object in the Reminder object.
        '''
        invalid_format = 'Ogiltigt format, försök igen. Exempel:\n\n**Hej rob, kan '\
                        'du komma ihåg; händelse, 2019-01-01-09:00, plats**.\n\nDet är '\
                        'viktigt att ange ett semikolon och sedan separera med '\
                        'mellanslag och kommatecken. Datumformatet måste vara '\
                        'ÅR-MÅNAD-DAG-TIMME:MINUT.'

        success = 'Det ska jag påminna om :smiley:'

        try:
            task = message.content.split(';')[-1].split(', ')
            body = task[0]
            event_date = datetime.strptime(task[1].strip(), '%Y-%m-%d-%H:%M')
            location = task[2]
        except Exception as e:
            return invalid_format
        else:
            self.reminder.add(Event(
                body = body, location = location, 
                date = event_date.date(), 
                time = time(hour = event_date.hour, minute = event_date.minute),
                alarm = timedelta(hours = 1)))
        return success

    def _get_adjective_response(self, message):
        '''
        Return a response with an adjective recieved,tagging 
        the user and returning the phrase back to the user.
        '''

        suffixes = (
            ', oftast i alla fall :smirk:', 
            '... ibland :sunglasses:', ':laughing:',
            ':slight_smile:'
        ) 
        suffix = choice(suffixes)
        phrase = str(message.content.split('är')[-1]).strip()
        return f'{message.author.mention} du är {phrase} {suffix}' 

    def _get_remembered_events(self):
        '''
        Return a friendly phrase for every saved event in memory.
        Sort by curriculum events only (auto generated Events representing
        scheduled class lessons and events from Schedule object.)
        '''
        remembered_events = None

        if self.reminder.events:
            remembered_events = [i for i in self.reminder.events if not i.curriculum_event]
        
        if remembered_events:
            remembered_events.sort(key = attrgetter('date'))
            remembered_events = [str(i) for i in remembered_events]
            return '\n'.join(remembered_events)
        return f'Inga sparade händelser :cry:'

    def _get_timenow_response(self):
        '''
        Return current timestamp in Hour:Minute format
        '''
        return f'Den är {datetime.now().strftime("%H:%M")}!'

    def _get_websearch_response(self, message):
        '''
        Return URL link fetched from the Websearch object.
        If no results were found, return phrase that indicates
        this to the user.
        '''
        query = message.content.split('rob')[-1].strip()
        result = self.websearch.search(query)

        if result is None:
            return 'Hmm.. hittade inget på det. Prova på engelska! :slight_smile:'
        return result

    def _joke(self):
        '''
        Return a random url or random joke phrase parsed
        from reddits api client 'praw'. Ensure that the returned
        joke is sub 2000 characters and randomize the choice between
        the two alternatives, r/jokes and r/programmerhumor
        '''

        iterations = 0
        iteration_limit = 10

        while True:
            iterations += 1
            joke_selection = randint(0, 1)

            if joke_selection == 0:
                submission = self.reddit.subreddit('jokes').random()
                message = f'{submission.title}\n||{submission.selftext}||'
            else:
                submission = self.reddit.subreddit('ProgrammerHumor').random()
                message =  f'{submission.title}\n{submission.url}'
            
            if len(message) < Brain.DISCORD_MSG_LENGTH_LIMIT:
                break
            elif iterations == iteration_limit:
                message = f'Jag kommer inte på något... :cry:'
                break
        return message

    def _interpret(self, message = str):
        '''
        If the bot is given a message, evaluate what it cntains.    
        Provide sufficient response to the given message by using
        class methods to get data for each response. Return enum
        instance, depending on which keyword matches which key in 
        the keyword dict property. Action will be taken accordingly
        by separate method.
        '''
        for keyword in Brain.KEYWORDS.keys():
            if keyword in message:
                action = Brain.KEYWORDS[keyword]
                return action
        return False

    @property
    def next_lesson_response(self):
        return self._get_next_lesson_response()

    @property
    def commands(self):
        return self._commands
    
    @commands.setter
    def commands(self, value = str):
        self._commands = value