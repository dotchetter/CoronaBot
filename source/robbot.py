import os
import json
from custom_errs import *
from enum import Enum, auto
from datetime import datetime, time, timedelta
from schedule import Schedule, Event
from reminder import Reminder
from random import choice
from operator import attrgetter
from dataclasses import dataclass
from pathlib import Path


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

@dataclass
class UnrecognizedCommand:
    '''
    Represent a message recieved in chat that the bot
    was unable to handle. Store message content, author
    and when it was recieved.
    '''
    command: str
    author: str
    timestamp: None

    @property
    def timestamp(self):
        return self.timestamp

    @timestamp.setter
    def timestamp(self, value):
        if isinstance(value, datetime):
            self.timestamp = value.isoformat()

class ResponseOptions(Enum):
    '''
    Constant enumerators for matching keywords against when
    deciding which response to give a given command to the bot.
    '''
    NEXT_LESSON = auto()
    TODAYS_LESSONS = auto()
    SCHEDULE = auto()
    SHOW_BOT_COMMANDS = auto()
    MEANING_OF_LIFE = auto()
    REMEMBER_EVENT = auto()
    SHOW_EVENTS = auto()
    EXPLICIT = auto()

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
        '?',
        'Jag fattar inte riktigt.',
        'Mjaa det låter bra!',
        'Alltid, alltid. Självklart.',
        'Ja visst!',
        'Jag håller med.',
        'Ingen aning vad du pratar om.'
    )
    
    EXPLICIT_ADJECTIVES = [
        'ful',
        'dum',
        'ass',
        'suger'
    ]
    
    KEYWORDS = {
        'klass rum': ResponseOptions.NEXT_LESSON,
        'klassrum': ResponseOptions.NEXT_LESSON,
        'nästa lektion': ResponseOptions.NEXT_LESSON,
        'lektioner idag': ResponseOptions.TODAYS_LESSONS,
        'dagens lektioner': ResponseOptions.TODAYS_LESSONS,
        'lektioner': ResponseOptions.TODAYS_LESSONS,
        'vad kan du': ResponseOptions.SHOW_BOT_COMMANDS,
        'schema': ResponseOptions.SCHEDULE,
        'meningen med livet': ResponseOptions.MEANING_OF_LIFE,
        'kan du komma ihåg': ResponseOptions.REMEMBER_EVENT,
        'kan du påminna om': ResponseOptions.REMEMBER_EVENT,
        'kan du påminna': ResponseOptions.REMEMBER_EVENT,
        'tenta': ResponseOptions.SHOW_EVENTS,
        'tentor': ResponseOptions.SHOW_EVENTS,
        'händelser': ResponseOptions.SHOW_EVENTS,
        'event': ResponseOptions.SHOW_EVENTS,
        'events': ResponseOptions.SHOW_EVENTS,
        'aktiviteter': ResponseOptions.SHOW_EVENTS,
        'skit': ResponseOptions.EXPLICIT,
        'helvete': ResponseOptions.EXPLICIT,
        'fuck': ResponseOptions.EXPLICIT,
        'du suger': ResponseOptions.EXPLICIT,
        'du luktar': ResponseOptions.EXPLICIT,
        'kiss my': ResponseOptions.EXPLICIT,
    }
    
    def __init__(self, schedule_url = str, hourdelta = int):
        self.schedule = Schedule(schedule_url)
        self.schedule.adjust_event_hours(hourdelta = hourdelta)
<<<<<<< HEAD
<<<<<<< HEAD
        self._commands = self._get_bot_commands()
        self._explicit_response = self._get_explicit_response()

=======
        self.reminder = Reminder()
        self._commands = self._get_bot_commands()
        self._unrecognized_commands = []
>>>>>>> 6c0d67f6008a021431b7bc2bebc802162c193867
=======
        self.reminder = Reminder()
        self._commands = self._get_bot_commands()
        self._unrecognized_commands = []
>>>>>>> upstream/master

    def respond_to(self, message):
        '''
        Call private interpretation method to get enum instance
        which points toward which response to give. 
        '''

        interpretation = self._interpret(message = message.content)
        
        if not interpretation:
            self._log_unrecognized_message(message)
            return f'{choice(Brain.MISUNDERSTOOD_PHRASES)}\r\n' \
                    '**Psst**: Skriv "Hej Rob, vad kan du?"'

        if interpretation == ResponseOptions.NEXT_LESSON:
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
        elif interpretation == ResponseOptions.EXPLICIT:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            response = self.__get_explicit_response(message,messageUser)

=======
            response = self.explicit_response
>>>>>>> upstream/master
=======
            response = self._get_explicit_response(message)

>>>>>>> 6c0d67f6008a021431b7bc2bebc802162c193867
=======
            response = self._get_explicit_response(message)

>>>>>>> upstream/master
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
        discord_msg_length_limit = 2000
        last_date = self.schedule.curriculum[0].begin.date()
        
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
    
                if (discord_msg_length_limit - len(phrase)) > 10:
                    friendly_schedule.append(phrase)
                    discord_msg_length_limit -= len(phrase)
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

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    def __get_explicit_response(self,message,messageUser):
        '''
        Return an explicit response if people are being mean.
        '''
        messageList = message.split()
        for word in messageList:
            if word in self._explicitAdjectives:
                explicitAdjective = word
            else:
                continue
        return f'<@{messageUser}> är {explicitAdjective}'
        
        # with open('explicit_responses.dat', 'r', encoding = 'utf-8') as f:
        #     responses = f.readlines()
        # return choice(responses)
=======
    def _get_explicit_response(self):
        '''
        Return an explicit response if people are being mean.
        '''
        with open('explicit_responses.dat', 'r', encoding = 'utf-8') as f:
            responses = f.readlines()
        return responses
>>>>>>> upstream/master
=======
    def _get_explicit_response(self, message):
        '''
        Return an explicit response if people are being mean.
        '''
        for word in message.content.split():
            if word in Brain.EXPLICIT_ADJECTIVES:
                return f'{message.author.mention} är {word}' 
>>>>>>> 6c0d67f6008a021431b7bc2bebc802162c193867
=======
    def _get_explicit_response(self, message):
        '''
        Return an explicit response if people are being mean.
        '''
        for word in message.content.split():
            if word in Brain.EXPLICIT_ADJECTIVES:
                return f'{message.author.mention} är {word}' 
>>>>>>> upstream/master

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

        for keyword in Brain.EXPLICIT_ADJECTIVES:
            if keyword in message:
                return ResponseOptions.EXPLICIT
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