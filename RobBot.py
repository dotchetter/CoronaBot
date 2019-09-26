import ics
import json
import os
from datetime import datetime, timedelta
from urllib.request import urlopen

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

Dependencies:
    Non-standard lib:
    * dotenv
    * discord
'''

class MetaFileError(Exception):
	__module__ = 'RobBot'

class Schedule:
	'''
	Parse an .ics url and fetch the data for this calendar.
	The data will be used to return classroom for the day,
	the day after and similar requests in a simple format 
	with properties.
	'''
	def __init__(self, url):
		self._url = url
		self._calendar = ics.Calendar(urlopen(self._url).read().decode())
	
	@property
	def today(self):
		return datetime.now().date()

	@property
	def current_time(self):
		return datetime.now()

	@property
	def schedule(self):
		_schedule = list(self._calendar.events)
		_schedule.sort()
		return _schedule

	@property
	def todays_lessons(self):
		lessons = [i for i in self.schedule if i.begin.date() == self.today] 
		if len(lessons):
			return lessons
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
		if self.todays_lessons:
			for lesson in self.todays_lessons:
				if self.current_time < (lesson.begin.time() + timedelta(hours = 2)):
					return lesson
		else:
			for lesson in self.schedule:
				if lesson.begin.date() > self.today:
					return lesson

	@property
	def next_lesson_classroom(self):
		_next_lesson = self.next_lesson
		return _next_lesson.location
	

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
	def __init__(self, name = str):
		self._name = name
		self._keywords = self.__parse_keywords_fromjson()
		self._reference_file = 'ref.json'
		self.awakesince = datetime.now()
		
		if not os.path.isfile(self._reference_file):
			raise Exception('')

	def respond_to_message(self, message = str):
		'''
		If the bot is given a message, evaluate what it contains.
		Provide sufficient response to the given message.
		'''
		_keywords = self.__parse_keywords_fromjson()
		if _keywords[0] in message:
			pass

	def __parse_keywords_fromjson(self):
		'''
		Load and parse a locally stored .json with 
		keywords, phrases, and other data stored in
		strings. This method returns keywords that the
		human can use when chatting with the bot, giving
		us a hint what the human wants from the bot.
		'''
		try:
			with open(self._reference_file, 'r') as f:
				return json.loads(file.read(), encoding = 'utf-8')
		except Exception as e:
			raise MetaFileError('Could not read data from meta file')
			return False


	@property
	def awakesince(self):
		return self._awakesince.strftime("%Y-%m-%d-%H:%m:%S") 

	@awakesince.setter
	def awakesince(self, value = None):
		self._awakesince = value