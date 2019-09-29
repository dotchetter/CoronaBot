import json
import os
from custom_errs import *
from enum import Enum
from datetime import datetime
from schedule import Schedule
from dataclasses import dataclass

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
	def __init__(self, name = str, schedule_url = str):
		self._name = name
		self.schedule = Schedule(schedule_url)
		self.schedule.adjust_event_hours(add_hours = 2)
		self.awakesince = datetime.now()
		self._mock_keywords = {
			'klassrum': ResponseOptions.NEXT_LESSON,
			'nästa lektion': ResponseOptions.NEXT_LESSON,
			'lektioner idag': ResponseOptions.TODAYS_LESSONS,
			'dagens lektioner': ResponseOptions.TODAYS_LESSONS,
			'vad kan du?': ResponseOptions.SHOW_BOT_COMMANDS,
			'schema': ResponseOptions.SCHEDULE,
			'meningen med livet': ResponseOptions.MEANING_OF_LIFE
		}

	def respond_to(self, message = str):
		'''
		Call private interpretation method to get enum instance
		which points toward which response to give. 
		'''
		misunderstood_phrase = ':thinking:..? Skriv "Hej Rob, vad kan du?" för att se mina tricks!'

		interpretation = self.__interpret(message = message)

		if interpretation.name == 'NEXT_LESSON':
			response = self.__get_next_lesson_response()
		elif interpretation.name == 'TODAYS_LESSONS':
			response = self.__get_todays_lessons_phrase()
		elif interpretation.name == 'SCHEDULE':
			response = self.__get_schedule_phrase()
		elif interpretation.name == 'SHOW_BOT_COMMANDS':
			response = self.__get_bot_commands()
		elif interpretation.name == 'MEANING_OF_LIFE':
			response = '42'
		else:
			response = misunderstood_phrase

		return response

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
			return f'Här är schemat för dagen:\n{ self.schedule.todays_lessons}'
		return 'Det finns inga lektioner på schemat för idag :sunglasses:'

	def __get_schedule_phrase(self):
		'''
		Return string with the schedule for as long as forseeable
		with Schedule object. 
		'''
		return f'Här är schemat så långt jag kan se:\n{self.schedule.schedule}'


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
		return f'Nästa lektion är i {classroom}, {date}, kl {hour} :smile:'


	def __interpret(self, message = str):
		'''
		If the bot is given a message, evaluate what it cntains.	
		Provide sufficient response to the given message by using
		class methods to get data for each response. Return enum
		instance, depending on which keyword matches which key in 
		the keyword dict property. Action will be taken accordingly
		by separate method.
		'''
		for keyword in self._mock_keywords.keys():
			if keyword in message:
				action = self._mock_keywords[keyword]
				return action
		return False

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