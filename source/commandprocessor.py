from enum import Enum, auto
from dataclasses import dataclass
from abc import ABC, abstractmethod
from source.schedule import Schedule

import timeit



'''
Details:
    2019-12-23

Module details:
    Application backend logic; Discord bot intelligence
    apeech parsing module. Try to understand the composition
    of sentences and provide a directive for what kind of
    response to provide from said command.
'''

class ResponseOptions(Enum):
    '''
    Constant enumerators for matching keywords against when
    deciding which response to give a given command to the bot.
    '''
    SCHEDULE_NEXT_LESSON = auto()
    SCHEDULE_TODAYS_LESSONS = auto()
    SCHEDULE_TOMORROWS_LESSONS = auto()
    SCHEDULE_SCHEDULE = auto()
    REMINDER_REMEMBER_EVENT = auto()
    REMINDER_SHOW_EVENTS = auto()
    ADJECTIVE = auto()
    TELL_JOKE = auto()
    TIMENOW = auto()
    WEBSEARCH = auto()
    LUNCH_TODAY = auto()
    LUNCH_TOMORROW = auto()
    LUNCH_FOR_WEEK = auto()
    SHOW_BOT_COMMANDS = auto()
    UNIDENTIFIED = auto()

class CommandCategory(Enum):
	'''
	Various commands that are supported. 
	'''
	LUNCH_MENU = auto()
	TELL_JOKE = auto()
	SCHEDULE = auto()
	REMINDER = auto()
	WEB_SEARCH = auto()
	PERSONAL = auto()
	UNIDENTIFIED = auto()

class CommandPronouns(Enum):
	'''
	Identifiable pronouns in recieved commands.
	__lt__ is implemented in order for a sorted
	set of instances to be returned.
	'''
	INTERROGATIVE = auto()
	PERSONAL = auto()
	POSSESSIVE = auto()
	UNIDENTIFIED = auto()

	def __lt__(self, other):
		return self.value < other.value

class PronounLookupTable:
	'''
	Provide a grammatic framework that 
	returns a tuple of matches for certain
	grammatic classes of words found in a given
	sentence. 
	'''
	def __init__(self):
		self._lookup_table = {
			CommandPronouns.INTERROGATIVE: (
				'vad', 'vem', 
				'hur', 'varför',
				'vilken', 'vilket',
				'hurdan', 'hurudan',
				'undrar', 'när'),

			CommandPronouns.PERSONAL: (
				'jag', 'vi',
				'du', 'ni',
				'han', 'hon',
				'den', 'de', 
				'dem'),

			CommandPronouns.POSSESSIVE: (
				'mitt', 'mina',
				'min', 'vårt',
				'vår', 'våra',
				'vårt', 'din',
				'ditt', 'dina',
				'ert', 'er',
				'era', 'sin',
				'sitt', 'sina')
		}

	def lookup(self, sentence = []):
		'''
		Split a given string by space if present, to iterate
		over a sentence of words. Returns a list with enum
		instances representing the pronouns that make up the
		composition of the string received. 
		'''
		pronouns = []

		for word in sentence:
			for key in self._lookup_table:
				if word in self._lookup_table[key]:
					pronouns.append(key)
			if '?' in word:
				pronouns.append(CommandPronouns.INTERROGATIVE)
					
		if len(pronouns):
			return sorted(set(pronouns))
		return [CommandPronouns.UNIDENTIFIED]

class FeatureCommandIdentifier(ABC):
	'''
	Describe a data structure that binds certain
	keywords to a certain feature. As the feature
	stack grows, this class must be inherited from
	with abstract methods and keyword tuple.
	'''
	IGNORED_CHARS = '?=)(/&%¤#"!,.-;:_^*`´><|'

	def __init__(self):
		super().__init__()
		self._keywords = tuple()
		self._subcategories = dict()

	def __contains__(self, other):
		return other in self._keywords

	@abstractmethod
	def __getitem__(self, item):
		pass

	def get_subcategory(self, message):
		for word in message:
			word = word.strip(FeatureCommandIdentifier.IGNORED_CHARS)
			if word in self._subcategories:
				return self._subcategories[word]
		return ResponseOptions.UNIDENTIFIED

class LunchMenuCommandIdentifier(FeatureCommandIdentifier):
	def __init__(self):
		super().__init__()
		self._keywords = (
			'lunch', 'mat',
			'käk', 'krubb',
			'föda', 'tugg'
		)

		self._subcategories = {
			'idag': ResponseOptions.LUNCH_TODAY,
			'imorgon': ResponseOptions.LUNCH_TOMORROW,
			'imorn': ResponseOptions.LUNCH_TOMORROW,
			'imorron': ResponseOptions.LUNCH_TOMORROW,
			'imorrn': ResponseOptions.LUNCH_TOMORROW,
			'vecka': ResponseOptions.LUNCH_FOR_WEEK,
			'veckan': ResponseOptions.LUNCH_FOR_WEEK
		}

	def __getitem__(self, iterable):
		for word in iterable:
			if word.strip(FeatureCommandIdentifier.IGNORED_CHARS) in self:
				return CommandCategory.LUNCH_MENU

	def get_subcategory(self, message):
		for word in message:
			word = word.strip(FeatureCommandIdentifier.IGNORED_CHARS)
			if word in self._subcategories:
				return self._subcategories[word]
		return ResponseOptions.LUNCH_TODAY


class JokeCommandIdentifier(FeatureCommandIdentifier):
	def __init__(self):
		super().__init__()
		self._keywords = (
			'skämt', 'meme',
			'skoja', 'skoj',
			'humor', 'roligt',
			'skämta'
		)

		self._subcategories = {
			'meme': ResponseOptions.TELL_JOKE,
			'skämt': ResponseOptions.TELL_JOKE,
			'skämta': ResponseOptions.TELL_JOKE,
			'skoja': ResponseOptions.TELL_JOKE,
			'skoj': ResponseOptions.TELL_JOKE,
			'humor': ResponseOptions.TELL_JOKE,
			'roligt': ResponseOptions.TELL_JOKE
		}
	
	def __getitem__(self, iterable):
		for word in iterable:
			if word.strip(FeatureCommandIdentifier.IGNORED_CHARS) in self:
				return CommandCategory.TELL_JOKE
	
	
class ScheduleCommandIdentifier(FeatureCommandIdentifier):
	def __init__(self):
		super().__init__()
		self._keywords = (
			'schema', 'schemat',
			'lektion', 'klassrum',
			'sal', 'lektioner',
			'lektion'
		)

		self._subcategories = {
			'nästa': ResponseOptions.SCHEDULE_NEXT_LESSON,
			'klassrum': ResponseOptions.SCHEDULE_NEXT_LESSON,
			'idag': ResponseOptions.SCHEDULE_TODAYS_LESSONS,
			'imorgon': ResponseOptions.SCHEDULE_TOMORROWS_LESSONS,
			'schema': ResponseOptions.SCHEDULE_SCHEDULE,
			'schemat': ResponseOptions.SCHEDULE_TOMORROWS_LESSONS
		}

	def __getitem__(self, iterable):
		for word in iterable: 
			if word.strip(FeatureCommandIdentifier.IGNORED_CHARS) in self:
				return CommandCategory.SCHEDULE
	
	
class ReminderCommandIdentifier(FeatureCommandIdentifier):
	def __init__(self):
		super().__init__()
		self._keywords = (
			'ihåg', 'memorera',
			'spara', 'påminna',
			'påminnelse', 'event',
			'events', 'påminnelser'
		)

		self._subcategories = {
			'ihåg': ResponseOptions.REMINDER_REMEMBER_EVENT,
			'påminna': ResponseOptions.REMINDER_REMEMBER_EVENT,
			'event': ResponseOptions.REMINDER_SHOW_EVENTS,
			'påminnelser': ResponseOptions.REMINDER_SHOW_EVENTS,
			'aktiviteter': ResponseOptions.REMINDER_SHOW_EVENTS
		}

	def __getitem__(self, iterable):
		for word in iterable: 
			if word.strip(FeatureCommandIdentifier.IGNORED_CHARS) in self:
				return CommandCategory.REMINDER

@dataclass
class Interpretation:
	'''
	This object represents the output from the
	CommandProcessor class, where this instance
	represents the action to take, after parsing
	and trying to understand the command, question
	or other sentence body that was provided.
	'''
	command_type: set(CommandPronouns)
	response: str
	original_message: str

class CommandProcessor:
	'''
	This object, while integrated to a front end
	works as a way to parse and understand what a
	human is asking for. An object containing the 
	representation of the interpretation of said
	sentence or word is returned of class 
	Interpretation.
	'''
	def __init__(self):
		self._pronoun_lookup_table = PronounLookupTable()
		self._command_variations = []
		self._schedule = Schedule('https://cloud.timeedit.net/nackademin/web/1/ri6555Qy1446n6QZ0YQ4Q7ZQZ5607.ics')
		
		self._lunch_menu_command_identifier = LunchMenuCommandIdentifier()
		self._joke_command_identifier = JokeCommandIdentifier()
		self._schedule_command_identifier = ScheduleCommandIdentifier()
		self._reminder_command_identifier = ReminderCommandIdentifier()

		self._category_identifiers = (
			self._reminder_command_identifier,
			self._lunch_menu_command_identifier,
			self._joke_command_identifier,
			self._schedule_command_identifier
		)

	def _interpret(self, message):
		'''
		Pass the message to key featrure identifier objects
		first. If a match is found, an enum for this feature
		is returned inside an Interpretation object. If no
		match is found, a prioritized evaluation is made on
		the message, whether it contains a personal meaning 
		or if it is a more widely asked question which means
		a web search is in order. Since the latter is to be 
		least assumed, it is placed last.
		'''
		found_pronouns = self._pronoun_lookup_table.lookup(message)

		for identifier in self._category_identifiers:
			response_category = identifier[message]
			if response_category:
				return Interpretation(found_pronouns, response_category, message)
					
		if CommandPronouns.PERSONAL in found_pronouns:
			return Interpretation(found_pronouns, CommandCategory.PERSONAL, message)
		elif CommandPronouns.INTERROGATIVE in found_pronouns:
			return Interpretation(found_pronouns, CommandCategory.WEB_SEARCH, message)
		return Interpretation(found_pronouns, CommandCategory.UNIDENTIFIED, message)

	def process(self, message = str):
		'''
		Process an Interpretation object, and evaluate
		a sufficient response phrase for a given
		Interpretation object instance, depending upon
		command type, identified pronouns and identified
		response.
		'''
		message = message.lower().split(' ')
		interpretation = self._interpret(message)
	
		if interpretation.response == CommandCategory.LUNCH_MENU:
			return self._lunch_menu_command_identifier.get_subcategory(message)
		elif interpretation.response == CommandCategory.SCHEDULE:
			return self._schedule_command_identifier.get_subcategory(message)
		elif interpretation.response == CommandCategory.TELL_JOKE:
			return self._joke_command_identifier.get_subcategory(message)
		elif interpretation.response == CommandCategory.REMINDER:
			return self._reminder_command_identifier.get_subcategory(message)
		elif CommandPronouns.INTERROGATIVE in interpretation.command_type:
			return ResponseOptions.WEBSEARCH
		return ResponseOptions.UNIDENTIFIED

	@staticmethod
	def wrap(func):
		def inner():
			return func
		return inner

if __name__ == '__main__':

	processor = CommandProcessor()
	while True:
		cmd = input('-> ')
		if not len(cmd): 
			continue
		print(f'chatbot: {processor.process(cmd).name}\n')