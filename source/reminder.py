from datetime import datetime, time
from schedule import Weekdays

'''
Details:
    2019-10-14

Module details:
    Reminders
    When an item approaches, this represents a reminder.

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class schedule and then
    share the current classroom for the day or week in the chat
    with a chatbot. 
'''


class Reminder:
	'''
	Keep track of Event instances and return an event that 
	matches current date and second upon query.
	'''
	def __init__(self):
		self._events = []
		self._reoccuring = []

	def purge(self):
		purged_events = []

		for item in self._events:
			if item.datetime < datetime.now():
				purged_events.append(item)
				self._events.remove(item)

		return purged_events

	def add(self, event):
		self._events.append(event)

	def add_reoccuring(self, event):
		self._reoccuring.append(event)

	@property
	def events(self):
		if len(self._events):
			return self._events
		return None
	
	@property
	def reoccuring(self):
		if len(self._reoccuring):
			return self._reoccuring
		return None

	def get(self):
		now = datetime.now()
		
		now_time = time(
			hour = now.hour, 
			minute = now.minute,
			second = now.second)
		
		for day in Weekdays:
			if now.isoweekday() == day.value:
				today = day

		if self.events:
			for event in self.events:
				if event.time == now_time and event.datetime == now.date():
					return event

		if self.reoccuring:
			for event in self.reoccuring:
				for weekday in event.weekdays:
					if weekday == today and now_time == event.time:
						return event
		return None