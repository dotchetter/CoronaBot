import ics
import json
from custom_errs import *
from datetime import date, datetime, timedelta, time

'''
Details:
    2019-09-25

Module details:
    Event
    This class is used to represent an event, in any given form.
    It is currently mainly used for repsesenting a class in school,
    a re-occuring event, or an event created by a user in-chat.

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class curriculum and then
    share the current classroom for the day or week in the chat
    with a chatbot. 
'''

class Event:
    def __init__(self, *args, **kwargs):
        self.body = None
        self.location = None
        self.date = None
        self.curriculum_event = False
        self.weekdays = []
        self.time = time()
        self.alarm = timedelta()

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self):
        what = self.body
        where = self.location
        
        if self.date:
            when = f'{self.date} - {self.time.strftime("%H:%M")}'
        else:
            when = self.time.strftime("%H:%M")
        
        return f'Vad: {what}\nNär: {when}\nVar: {where}\n'

    @property
    def curriculum_event(self):
        return self._curriculum_event

    @curriculum_event.setter
    def curriculum_event(self, value):
        self._curriculum_event = value    

    @property
    def body(self):
        if self._body:
            return self._body
        return '-'

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def location(self):
        if self._location:
            return self._location
        return '-'

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def weekdays(self):
        if self._weekdays:
            return self._weekdays
        return []
    
    @weekdays.setter
    def weekdays(self, value):
        if isinstance(value, list):
            self._weekdays = value
        else:
            raise AttributeError(f'Expected {list}, got {type(value)}')

    @property
    def time(self):
        return self._time
        
    @time.setter
    def time(self, value):
        if isinstance(value, time):
            self._time = value
        else:
            raise AttributeError(f'Expected {time}, got {type(value)}')

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if isinstance(value, date) or isinstance(value, type(None)):
            self._date = value
        else:
            raise AttributeError(f'Expected {date} or {None}, got {type(value)}')

    @property
    def alarm(self):
        return self._alarm

    @alarm.setter
    def alarm(self, value):
        if isinstance(value, timedelta):
            try:
                combined = datetime.combine(datetime.today(), self.time)
                self._alarm = (combined - value).time()
            except Exception as e:
                raise EventReminderTimeAdjustError(e)
        else:
            raise AttributeError(f'Expected {timedelta}, got {type(value)}')

    def to_json(self):
        return json.dumps(
            self, default = lambda: self.__dict__,
            sort_keys = True, ensure_ascii = False, 
            indent = 4)