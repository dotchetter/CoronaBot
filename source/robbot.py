import os
from custom_errs import *
from enum import Enum
from datetime import datetime, time
from schedule import Schedule, Event
from random import choice

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

class ResponseOptions(Enum):
    '''
    Constant enumerators for matching keywords against when
    deciding which response to give a given command to the bot.
    '''
    NEXT_LESSON = 0
    TODAYS_LESSONS = 1
    SCHEDULE = 2
    SHOW_BOT_COMMANDS = 3
    MEANING_OF_LIFE = 4
    REMEMBER_ACTIVITY = 5
    SHOW_ACTIVITY = 6
    EXPLICIT = 7

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
    def __init__(self, name = str, schedule_url = str, hourdelta = int):
        self._name = name
        self.schedule = Schedule(schedule_url)
        self.schedule.adjust_event_hours(hourdelta = hourdelta)
        self.commands = self.__get_bot_commands()
        self._keywords = {
            'klass rum': ResponseOptions.NEXT_LESSON,
            'klassrum': ResponseOptions.NEXT_LESSON,
            'nästa lektion': ResponseOptions.NEXT_LESSON,
            'lektioner idag': ResponseOptions.TODAYS_LESSONS,
            'dagens lektioner': ResponseOptions.TODAYS_LESSONS,
            'vad kan du': ResponseOptions.SHOW_BOT_COMMANDS,
            'schema': ResponseOptions.SCHEDULE,
            'meningen med livet': ResponseOptions.MEANING_OF_LIFE,
            'kan du komma ihåg': ResponseOptions.REMEMBER_ACTIVITY,
            'händelser': ResponseOptions.SHOW_ACTIVITY,
            'vilka events': ResponseOptions.SHOW_ACTIVITY,
            'event': ResponseOptions.SHOW_ACTIVITY,
            'events': ResponseOptions.SHOW_ACTIVITY,
            'aktiviteter': ResponseOptions.SHOW_ACTIVITY,
            'skit på dig': ResponseOptions.EXPLICIT,
            'åt helvete': ResponseOptions.EXPLICIT,
            'fuck you': ResponseOptions.EXPLICIT,
            'fuck off': ResponseOptions.EXPLICIT,
            'du suger': ResponseOptions.EXPLICIT,
            'kiss my ass': ResponseOptions.EXPLICIT,
        }

    def respond_to(self, message = str):
        '''
        Call private interpretation method to get enum instance
        which points toward which response to give. 
        '''
        misunderstood_phrase = 'Jag fattar inte riktigt. Skriv "Hej Rob, vad kan du?"'
        interpretation = self.__interpret(message = message)
        if not interpretation:
            return misunderstood_phrase

        if interpretation == ResponseOptions.NEXT_LESSON:
            response = self.__get_next_lesson_response()
        elif interpretation == ResponseOptions.TODAYS_LESSONS:
            response = self.__get_todays_lessons_phrase()
        elif interpretation == ResponseOptions.SCHEDULE:
            response = self.__get_schedule_phrase()
        elif interpretation == ResponseOptions.SHOW_BOT_COMMANDS:
            response = self.commands
        elif interpretation == ResponseOptions.MEANING_OF_LIFE:
            response = '42'
        elif interpretation == ResponseOptions.REMEMBER_ACTIVITY:
            response = self.__remember_activity(message)
        elif interpretation == ResponseOptions.SHOW_ACTIVITY:
            response = self.__get_remembered_activities()
        elif interpretation == ResponseOptions.EXPLICIT:
            response = self.__get_explicit_response()

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

    def __get_bot_commands(self):
        '''
        Return string that shows the human what this bot can do, 
        and how to formulate a question.
        '''
        try:
            with open('commands.dat', 'r', encoding = 'utf-8') as f:
                return str().join(f.readlines())
        except FileNotFoundError:
            return 'Ett fel uppstod - jag hittar inte filen. Hjälp!'

    def __get_todays_lessons_phrase(self):
        '''
        Return concatenated response phrase with all lessons for 
        the current date. If none, return a message that explains
        no lessons for current date.
        '''
        if self.schedule.todays_lessons:
            lessons = '\n'.join(self.schedule.todays_lessons)
            return f'Här är schemat för dagen:\n{lessons}'
        return 'Det finns inga lektioner på schemat idag :sunglasses:'

    def __get_schedule_phrase(self):
        '''
        Return string with the schedule for as long as forseeable
        with Schedule object. Take in to acount the 2000 character
        message limit in Discord. Append only until the length
        of the total string length of all elements combined are within
        0 - 2000 in length.s
        '''
        friendly_schedule = []
        discord_msg_length_limit = 2000
        
        for index, event in enumerate(self.schedule.schedule):
            begin = event.begin.adjusted_time.strftime('%H:%M')
            end = event.end.adjusted_time.strftime('%H:%M')
            location = event.location
            name = event.name
            date = event.begin.date()
            phrase = f'**{name}**\n**Klassrum:** {location}\n**När:** {date} -- {begin}-{end}'
            
            if index % 2 != 0:
                phrase += '\n'

            if (discord_msg_length_limit - len(phrase)) > 10:
                friendly_schedule.append(phrase)
                discord_msg_length_limit -= len(phrase)
            else:
                break        
        friendly_schedule = '\n'.join(friendly_schedule)        
        return f'**Här är schemat!** :slight_smile:\n\n{friendly_schedule}'


    def __get_next_lesson_response(self):
        '''
        Return string with concatenated variable values to tell the
        human which is the next upcoming lesson.
        '''
        date = self.schedule.next_lesson_date
        hour = self.schedule.next_lesson_time
        classroom = self.schedule.next_lesson_classroom
        schedule =  self.schedule.schedule
        todays_lessons = self.schedule.todays_lessons
        return f'Nästa lektion är i {classroom}, {date}, kl {hour} :slight_smile:'

    def __remember_activity(self, message):
        '''
        If the bot recieves a message with proper syntax, create
        an Event instance. Save this object in the Schedule object.
        '''
        invalid_format_string = 'Ogiltigt format. Ange ett event formaterat enligt '\
                                f'detta exempel:\n\n**Hej rob, kan du komma ihåg; händelse, '\
                                '2019-01-01-09:00, plats**. Det är viktigt att ange ett '\
                                'semikolon och sedan separera med mellanslag och kommatecken. '\
                                'Notera att datumformatet måste vara ÅR-MÅNAD-DAG-TIMME:MINUT.'
        success_string = 'Det ska jag komma ihåg! :smiley:'

        try:
            task = message.split(';')[-1].split(', ')
            body = task[0]
            event_date = datetime.strptime(task[1].strip(), '%Y-%m-%d-%H:%M')
            location = task[2]

            self.schedule.add_activity(
                Event(
                    body = body, location = location, 
                    datetime = event_date, time = time(
                        hour = event_date.hour, 
                        minute = event_date.minute, 
                        second = 0
                    )
                )
            )
        except Exception as e:
            return invalid_format_string
        return success_string

    def __get_explicit_response(self):
        '''
        Return an explicit response if people are being mean.
        '''
        with open('explicit_responses.dat', 'r', encoding = 'utf-8') as f:
            responses = f.readlines()
        return choice(responses)

    def __get_remembered_activities(self):
        '''
        Return a friendly phrase for every saved activity in memory.
        '''
        output = []
        if self.schedule.activities:
            for activity in self.schedule.activities:
                what = f'**Händelse**: {activity.body}'
                when = f'**När**: {activity.datetime.strftime("%Y-%m-%d-%H:%M")}'
                where = f'**Var**: {activity.location}\n'
                output.append(f'{what}\n{when}\n{where}')
                output.sort(reverse = True)
            return '\n'.join(output)
        return f'Inga sparade händelser :cry:'

    def __interpret(self, message = str):
        '''
        If the bot is given a message, evaluate what it cntains.    
        Provide sufficient response to the given message by using
        class methods to get data for each response. Return enum
        instance, depending on which keyword matches which key in 
        the keyword dict property. Action will be taken accordingly
        by separate method.
        '''
        for keyword in self._keywords.keys():
            if keyword in message:
                action = self._keywords[keyword]
                return action
        return False

    @property
    def commands(self):
        return self._commands
    
    @property
    def next_lesson_response(self):
        return self.__get_next_lesson_response()

    @commands.setter
    def commands(self, value = str):
        self._commands = value