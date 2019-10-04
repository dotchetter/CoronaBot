import ics
import json
import os
from custom_errs import *
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from urllib.request import urlopen
from enum import Enum
from sys import platform
from operator import attrgetter

'''
Details:
    2019-09-25

Module details:
    Application backend logic; ics schedule URL parsing
    class with methods and properties to return relevant
    data for a schedule.

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class schedule and then
    share the current classroom for the day or week in the chat
    with a chatbot. 
'''

@dataclass
class Event:
    body: str = None
    location: str = None
    weekdays: [] = None
    time: time = None
    datetime: datetime = None

class Schedule:
    '''
    Parse an .ics url and fetch the data for this calendar.
    The data will be used to return classroom for the day,
    the day after and similar requests in a simple format 
    with properties.
    '''
    def __init__(self, url = str):
        self._url = url
        self._scheduled_events = []
        self._activities = []
        self.set_calendar()
        self.truncate_event_name()

    def schedule_events(self, *args):
        '''
        Save instances of event object instances.
        '''
        for event in args:
            self._scheduled_events.append(event)

    def add_activity(self, *args):
        '''
        Save Events that were saved by people through
        creating a reminder from chat dialog
        '''
        for activity in args:
            self._activities.append(activity)

    def remove_activities(self):
        '''
        Remove a given activity from self._activities
        if the date is exhausted
        '''
        removed = []
        if len(self._activities):
            for activity in self._activities:
                if self.current_time.date() > activity.datetime.date():
                    removed.append(activity)
                    self._activities.remove(activity)
        return removed
        
    def adjust_event_hours(self, hourdelta = int):
        '''
        Adjust the hour in a calendar event by (n) hours.
        Create a time() property for both the event begin and 
        event end, with corrected hour stamps according to hourdelta
        parameter. The instance attribute will be accessible through
        self.begin.time and self.end.time.
        '''
        for event in self.schedule:
            try:
                year = self.current_time.year
                month = self.current_time.month
                day = self.current_time.day
                
                begin_hour, begin_minute = event.begin.hour, event.begin.minute
                end_hour, end_minute = event.end.hour, event.end.minute

                begin_time = datetime(year, month, day, begin_hour, begin_minute)
                end_time = datetime(year, month, day, end_hour, end_minute)
                
                begin_time += timedelta(hours = hourdelta)
                end_time += timedelta(hours = hourdelta)

                event.begin.adjusted_time = time(begin_time.hour, begin_time.minute)
                event.end.adjusted_time = time(end_time.hour, end_time.minute)

            except ValueError as e:
                msg = f'Could not adjust {event} with {hourdelta} hrs: {e}'
                raise TimezoneAdjustmentError(msg)
        return True

    def set_calendar(self):
        '''
        Get data from the timeedit servers containing the
        schedule for class IoT19 2 weeks ahead. This callable
        will refresh the .ics Calendar object.
        '''
        try:
            calendar = ics.Calendar(urlopen(self._url).read().decode())
        except ValueError:
            msg = 'Could not parse calendar url, verify server status and access.'
            raise InvalidCalendarUrl(msg)
        self._calendar = calendar

    def truncate_event_name(self):
        '''
        Truncate sensitive name data in events, containing the
        name of the teacher holding the class. This will reduce
        the privacy issue of storing names in log files.
        '''

        for event in self.schedule:
            event.name = f"{event.name.split(',')[0]},{event.name.split(',')[-1]}"

    @property
    def activities(self):
        if len(self._activities):
            self._activities.sort(key = attrgetter('datetime'))
            return self._activities
        return None

    @property
    def scheduled_events(self):
        return self._scheduled_events

    @property
    def today(self):
        return datetime.now().date()

    @property
    def weekday(self):
        weekdays = {
            1:'monday',
            2:'tueday',
            3:'wednesday',
            4:'thursday',
            5:'friday',
            6:'saturday',
            7:'sunday'
        }
        return weekdays[self.today.isoweekday()]

    @property
    def current_time(self):
        return datetime.now()

    @property
    def schedule(self):
        _schedule = list(self._calendar.events)
        _schedule.sort()
        return _schedule

    @property
    def todays_events(self):
        return [i for i in self.schedule if i.begin.date() == self.today]
    
    @property
    def todays_lessons(self):
        '''
        Iterate through the lessons of today, return these in a friendly
        string with properties such as start and end time with locations.
        '''
        output = []

        if len(self.todays_events):
            for event in self.todays_events:
                name = event.name.split(',')[-1].strip()
                event_start = event.begin.adjusted_time.strftime('%H:%M')
                event_end = event.end.adjusted_time.strftime('%H:%M')
                output.append(f'{name}, {event_start} - {event_end} i {event.location}')
            return output
        return None

    @property
    def next_lesson(self):
        '''
        Evaluate what lesson is the next on schedule. Iterate
        through the list of lessons for today. Compare the current
        time with each lesson start time, return the upcoming one.
        Adjust for calendar timezone with 2hrs. If no lesson is found
        for today, iterate over the entire sorted schedule and return
        the first lesson that lies in the future.
        '''
        lesson = None

        if self.todays_events:
            for event in self.todays_events:
                if self.current_time.hour < event.begin.adjusted_time.hour:
                    lesson = event
                    break
        if not lesson:
            for event in self.schedule:
                if event.begin.date() > self.today:
                    lesson = event
                    break
        return lesson

    @property
    def next_lesson_classroom(self):
        return self.next_lesson.location

    @property
    def next_lesson_name(self):
        return self.next_lesson.name
    
    @property
    def next_lesson_time(self):
        return f'{self.next_lesson.begin.adjusted_time.strftime("%H:%M")}'

    @property
    def next_lesson_date(self):
        return f'{self.next_lesson.begin.date()}'