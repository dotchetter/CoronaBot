import ics
import json
import os
from custom_errs import *
from datetime import datetime, timedelta, time
from urllib.request import urlopen
from enum import Enum


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

class Schedule:
	'''
	Parse an .ics url and fetch the data for this calendar.
	The data will be used to return classroom for the day,
	the day after and similar requests in a simple format 
	with properties.
	'''
	def __init__(self, url = str):
		self._url = url
		self.set_calendar()

	def adjust_event_hours(self, add_hours = int):
		'''
		Adjust the hour in a calendar event by (n) hours. 
		Expect a datetime.time instance in event parameter.
		This will add a .hour and a .minute property to the 
		Calendar() objects passed to this method.
		'''
		for event in self.schedule:
			try:
				hour = event.begin.hour
				minute = event.begin.minute
				year = self.current_time.year
				month = self.current_time.month
				day = self.current_time.day
	
				event_datetime = datetime(year, month, day, hour, minute)
				event_datetime += timedelta(hours = add_hours)
				event.begin.hour = event_datetime.hour
				event.begin.minute = event_datetime.minute
			except ValueError as e:
				msg = f'Could not adjust {event} with {add_hours} hrs: {e}'
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
		friendly_output = []

		lessons = self.todays_events  
		if len(lessons):
			for lesson in lessons:
				if lesson.begin.minute < 10:
					minute = f'0{lesson.begin.minute}'
				else:
					minute = lesson.begin.minute	
				hour = lesson.begin.hour
				name = lesson.name.split(',')[-1].strip()
				friendly_time = f'{hour}:{minute}'
				location = lesson.location
				friendly_string = f'{name} klockan {friendly_time} i {location}'
				friendly_output.append(friendly_string)
			return friendly_output
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
				if self.current_time.hour < event.begin.hour:
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
		return f'{self.next_lesson.begin.hour}'

	@property
	def next_lesson_date(self):
		return f'{self.next_lesson.begin.date()}'
	