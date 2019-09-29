import json
import os
from custom_errs import *
from enum import Enum
from datetime import datetime

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
	NEXT_LESSON = True
	SCHEDULE = True
	TODAYS_LESSONS = True
	MEANING_OF_LIFE = 42


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
		self.awakesince = datetime.now()
		#self._keywords = self.__parse_keywords_fromjson()
		#self._reference_file = 'ref.json'
		self._mock_keywords = {
			'klassrum': ResponseOptions.NEXT_LESSON,
			'nästa lektion': ResponseOptions.NEXT_LESSON,
			'lektioner idag': ResponseOptions.SCHEDULE,
			'schema': ResponseOptions.SCHEDULE,
			'meningen med livet': ResponseOptions.MEANING_OF_LIFE
		}

		#if not os.path.isfile(self._reference_file):
		#	raise Exception('Vital bot chat phrase file missing!')


	def respond_do(self, message = str):
		'''
		Call private interpretation method to get enum instance
		which points toward which response to give. 
		'''
		pass

	def __interpret(self, message = str):
		'''
		If the bot is given a message, evaluate what it cntains.	
		Provide sufficient response to the given message by using
		class methods to get data for each response. Return enum
		instance, depending on which keyword matches which key in 
		the keyword dict property. Action will be taken accordingly
		by separate method.
		'''

		for keyword in self._mock_keywords: # DEV
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