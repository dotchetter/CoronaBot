import praw
import random
from os import system
from datetime import datetime, timedelta, time
from enum import Enum, auto
from dataclasses import dataclass
from abc import ABC, abstractmethod
from timeit import default_timer as timer

from source.schedule import Schedule
from source.scraper import Scraper
from source.reminder import Reminder
from source.websearch import Websearch
from source.redditjoke import RedditJoke
from source.event import Event
'''
Details:
    2019-12-23

Module details:
    Application backend logic; Discord bot intelligence
    apeech parsing module. Try to understand the composition
    of sentences and provide a directive for what kind of
    response to provide from said command.
'''

class CommandSubcategory(Enum):
    '''
    Constant enumerators for matching keywords against when
    deciding which response to give a given command to the bot.
    '''
    SCHEDULE_NEXT_LESSON = auto()
    SCHEDULE_TODAYS_LESSONS = auto()
    SCHEDULE_TOMORROWS_LESSONS = auto()
    SCHEDULE_CURRICULUM = auto()
    REMINDER_REMEMBER_EVENT = auto()
    REMINDER_SHOW_EVENTS = auto()
    ADJECTIVE = auto()
    TELL_JOKE = auto()
    TIMENOW = auto()
    WEBSEARCH = auto()
    LUNCH_TODAY = auto()
    LUNCH_YESTERDAY = auto()
    LUNCH_TOMORROW = auto()
    LUNCH_DAY_AFTER_TOMORROW = auto()
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

class CommandPronoun(Enum):
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
            CommandPronoun.INTERROGATIVE: (
                'vad', 'vem',
                'hur', 'varför',
                'vilken', 'vilket',
                'hurdan', 'hurudan',
                'undrar', 'när'),

            CommandPronoun.PERSONAL: (
                'jag', 'vi',
                'du', 'ni',
                'han', 'hon',
                'den', 'de',
                'dem'),

            CommandPronoun.POSSESSIVE: (
                'mitt', 'mina',
                'min', 'vårt',
                'vår', 'våra',
                'vårt', 'din',
                'ditt', 'dina',
                'ert', 'er',
                'era', 'sin',
                'sitt', 'sina')
        }

    def lookup(self, message: list) -> tuple:
        '''
        Split a given string by space if present, to iterate
        over a sentence of words. Returns a tuple with enum
        instances representing the pronouns that make up the
        composition of the string received. If none is found,
        a tuple with a single CommandPronoun.UNIDENTIFIED is 
        returned.
        '''
        pronouns = []

        for word in message:
            for key in self._lookup_table:
                if word in self._lookup_table[key]:
                    pronouns.append(key)
            if '?' in word:
                pronouns.append(CommandPronoun.INTERROGATIVE)

        if len(pronouns):
            return tuple(sorted(set(pronouns)))
        return (CommandPronoun.UNIDENTIFIED,)

@dataclass
class Interpretation:
    '''
    This object represents the output from the
    CommandProcessor class. 

    command_pronouns: A collection of pronouns
    identified in the message.

    command_category: A single instance of
    CommandCategory telling which feature the 
    message was ultimately matched against.

    command_subcategory: A single instance of
    CommandSubcategory telling which method the
    message was ultimately matched with.

    original_message: The original message in 
    a tuple, split by space.

    response: The callable object that was returned
    from the Feature.

    error: Any exception that was caught upon parsing
    the message.
    '''
    command_pronouns: tuple(CommandPronoun) = ()
    command_category: CommandCategory = None,
    command_subcategory: CommandSubcategory = None,
    original_message: tuple = ()
    response: callable = None
    error: Exception = None

class FeatureCommandParserABC(ABC):
    '''
    Describe a data structure that binds certain
    keywords to a certain feature. As the feature
    stack grows, this class is used as a template
    for base classes that work with decomposing 
    a message string, trying to understand its context
    and intent.
    '''
    IGNORED_CHARS = '?=)(/&%¤#"!,.-;:_^*`´><|'

    def __init__(self, *args, **kwargs):
        self.ignored_chars = dict()
        super().__init__()
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @abstractmethod
    def __contains__(self, word: str) -> bool:
        return

    @abstractmethod
    def ignore_all(self, char: str):
        pass

    @abstractmethod
    def get_category(self, message: list) -> CommandCategory:
        '''
        Iterate over the words in received message, and 
        see if any of the words line up with the keywords
        provided for an instance of this class. If a match
        is found, the CommandCategory of the instance should
        return, otherwise None.
        '''
        return
    
    @abstractmethod
    def get_subcategory(self, message: list) -> CommandSubcategory:
        '''
        Returns a ResponseOption enum type that indicates more 
        precisely which method for a feature that the command 
        is matched against. This method should be overloaded if 
        a different return behaviour in a no-match-found scenario
        is desired.
        '''
        return

    @property
    @abstractmethod
    def category(self):
        return
    
    @category.setter
    @abstractmethod
    def category(self, category: CommandCategory):
        pass

    @property
    @abstractmethod
    def keywords(self) -> tuple:
        return
    
    @keywords.setter
    @abstractmethod
    def keywords(self, keywords: tuple):
        pass

    @property
    @abstractmethod
    def subcategories(self) -> dict:
        return

    @subcategories.setter
    @abstractmethod
    def subcategories(self, subcategories: dict):
        pass

    @property
    @abstractmethod
    def ignored_chars(self) -> dict:
        return

    @ignored_chars.setter
    @abstractmethod
    def ignored_chars(self, table: dict):
        pass

class FeatureCommandParserBase(FeatureCommandParserABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __contains__(self, word: str) -> bool:
        return word in self._keywords

    def ignore_all(self, char: str):
        self.ignored_chars[char] = ''

    def get_category(self, message: list) -> CommandCategory:
        for key in self.ignored_chars:
            message = [word.replace(key, self._ignored_chars[key]) for word in message]

        for word in message:
            if word.strip(FeatureCommandParserBase.IGNORED_CHARS) in self:
                return self._category
        return None
    
    def get_subcategory(self, message: list) -> CommandSubcategory:
        for word in message.split(' '):
            word = word.strip(FeatureCommandParserBase.IGNORED_CHARS)
            if word in self._subcategories:
                return self._subcategories[word]
        return CommandSubcategory.UNIDENTIFIED

    @property
    def category(self):
        return self._category
    
    @category.setter
    def category(self, category: CommandCategory):
        if not isinstance(category, CommandCategory):
            raise TypeError(f'category must be CommandCategory, got {type(category)}')
        self._category = category

    @property
    def keywords(self) -> tuple:
        return tuple()
    
    @keywords.setter
    def keywords(self, keywords: tuple):
        if not isinstance(keywords, tuple):
            raise TypeError(f'keywords must be tuple, got {type(keywords)}')
        self._keywords = keywords

    @property
    def subcategories(self) -> dict:
        return dict()
    
    @subcategories.setter
    def subcategories(self, subcategories: dict):
        if not isinstance(subcategories, dict):
            raise TypeError(f'subcategories must be dict, got {type(subcategories)}')
        self._subcategories = subcategories

    @property
    def ignored_chars(self) -> dict:
        return self._ignored_chars

    @ignored_chars.setter
    def ignored_chars(self, table: dict):
        if not isinstance(table, dict):
            raise TypeError(f'category must be dict, got {type(table)}')
        self._ignored_chars = table
    
class LunchMenuFeatureCommandParser(FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_subcategory(self, message: list) -> CommandSubcategory:
        for word in message.split(' '):
            word = word.strip(FeatureCommandParserABC.IGNORED_CHARS)
            if word in self._subcategories:
                return self._subcategories[word]
        return CommandSubcategory.LUNCH_TODAY

class JokeCommandFeatureCommandParser(FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ScheduleFeatureCommandParser(FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ReminderFeatureCommandParser(FeatureCommandParserBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CommandProcessor:
    '''
    This object, while integrated to a front end
    works as a way to parse and understand what a
    human is asking for. An object containing the 
    representation of the interpretation of said
    sentence or word is returned of class 
    Interpretation.
    '''

    def __init__(self, pronoun_lookup_table: PronounLookupTable):
        self._pronoun_lookup_table = pronoun_lookup_table
        self._features = []

    def process(self, message: str) -> CommandSubcategory:
        message = message.lower().split(' ')
        interpretation = self._interpret(message)
        return interpretation

    def _interpret(self, message: list) -> Interpretation:

        mapped_features = self._find_pronoun_mapped_features(message)

        if CommandPronoun.PERSONAL in found_pronouns:
            return Interpretation(found_pronouns, CommandCategory.PERSONAL, message)
        return Interpretation(found_pronouns, CommandCategory.UNIDENTIFIED, message)

    def _find_pronoun_mapped_features(self, message: list) -> tuple:
        '''
        return tuple with features that matched the message
        pronoun set.
        '''
        any_in = lambda iter_a, iter_b: True if any([i in iter_a for i in iter_b]) else False
        mapped_features = []
        found_pronouns = self._pronoun_lookup_table.lookup(message)
        
        for feature in self._features:
            if any_in(found_pronouns, feature.mapped_pronouns):
                mapped_features.append(feature)
        return tuple(mapped_features)

    @property
    def features(self) -> tuple:
        return self._features
    
    @features.setter
    def features(self, features: tuple):
        if not isinstance(features, tuple):
            raise TypeError(f'expected tuple, got {type(features)}')

        for feature in features:
            if not isinstance(feature, FeatureABC):
                raise TypeError(f'All features must inherit from FeatureABC, got {type(feature)}')
            
        self._features = features

class FeatureABC(ABC):
    ''' 
    Represent the template for a complete and 
    ready-to-use feature. 
    '''
    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @abstractmethod
    def __call__(self, message: list):
        pass

     @property
    def mapped_pronouns(self) -> tuple:
        return

    @mapped_pronouns.setter
    def mapped_pronouns(self, pronouns: tuple):
        pass
    
    @property
    @abstractmethod
    def interface(self) -> object:
        return
    
    @interface.setter
    @abstractmethod
    def interface(self, interface: object):
        pass

    @property
    @abstractmethod
    def command_parser(self) -> FeatureCommandParserBase:
        return

    @command_parser.setter
    @abstractmethod
    def command_parser(self, command_parser: FeatureCommandParserBase):
        pass

    @property
    @abstractmethod
    def command_mapping(self) -> dict:
        return
    
    @command_mapping.setter
    @abstractmethod
    def command_mapping(self, command_mapping: dict):
        pass

    @property
    @abstractmethod
    def interactive_methods(self) -> list:
        return
    
    @interactive_methods.setter
    @abstractmethod
    def interactive_methods(self):
        pass

class FeatureBase(FeatureABC):
    '''
    Base class for features coupled to the chatbot. 
    Use this class as a base class to inherit from when
    connecting your feature's interface to the bot.
    '''

    def __init__(self, *args, **kwargs):
        self.interactive_methods = []
        super().__init__(*args, **kwargs)

    def __call__(self, message: list):
        try:
            command_subcategory = self._command_parser.get_subcategory(message)
            if self.command_mapping[command_subcategory] in self.interactive_methods:
                return lambda message = message: self.command_mapping[command_subcategory](message)
            return self.command_mapping[command_subcategory]
        except KeyError:
            raise NotImplementedError(f'no mapped function call for {command_subcategory} in self.')
    
    @property
    def mapped_pronouns(self) -> tuple:
        return self.mapped_pronouns

    @mapped_pronouns.setter
    def mapped_pronouns(self, pronouns: tuple):
        if not isinstance(pronouns, tuple):
            raise TypeError(f'pronouns must be enclosed in a tuple.')
        for i, item in enumerate(pronouns:
            if not isinstance(item, CommandPronoun):
                raise TypeError(f'object at index {i} is not a CommandPronoun.')

    @property
    def interface(self) -> object:
        return self._interface
    
    @interface.setter
    def interface(self, interface: object):
        self._interface = interface

    @property
    def command_parser(self) -> FeatureCommandParserBase:
        return self._command_parser

    @command_parser.setter
    def command_parser(self, command_parser: FeatureCommandParserBase):
        if not isinstance(command_parser, FeatureCommandParserBase):
            raise TypeError(f'command_parser must be FeatureCommandParserBase, got {type(command_parser)}')
        self._command_parser = command_parser

    @property
    def command_mapping(self) -> dict:
        return self._command_mapping
    
    @command_mapping.setter
    def command_mapping(self, command_mapping: dict):
        if not isinstance(command_mapping, dict):
            raise TypeError(f'command_parser must be dict, got {type(command_mapping)}')
        
        for key in command_mapping:
            if not isinstance(key, CommandSubcategory):
                raise TypeError(f'key must be CommandSubcategory, got {type(key)}')
            elif not callable(command_mapping[key]):
                raise TypeError(f'"{command_mapping[key]}" is not callable.')
        self._command_mapping = command_mapping

    @property
    def interactive_methods(self) -> list:
        return self._interactive_methods
    
    @interactive_methods.setter
    def interactive_methods(self, arg: list):
        if not isinstance(arg, list):
            raise TypeError(f'command_parser must be list, got {type(arg)}')
        self._interactive_methods = arg

class LunchMenuFeature(FeatureBase):

    FEATURE_KEYWORDS = (
        'lunch', 'mat',
        'käk', 'krubb',
        'föda', 'tugg'
    )

    FEATURE_SUBCATEGORIES = {
        'igår': CommandSubcategory.LUNCH_YESTERDAY,
        'idag': CommandSubcategory.LUNCH_TODAY,
        'imor': CommandSubcategory.LUNCH_TOMORROW,
        'imorgon': CommandSubcategory.LUNCH_TOMORROW,
        'imoron': CommandSubcategory.LUNCH_TOMORROW,
        'imorron': CommandSubcategory.LUNCH_TOMORROW,
        'imorrn': CommandSubcategory.LUNCH_TOMORROW,
        'övermorgon': CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW,
        'övermorn': CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW,
        'övermorrn': CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW,
        'vecka': CommandSubcategory.LUNCH_FOR_WEEK,
        'veckan': CommandSubcategory.LUNCH_FOR_WEEK
    }

    def __init__(self, **kwargs):
        today = lambda: datetime.now().weekday()
        
        self.command_parser = LunchMenuFeatureCommandParser(
            keywords = LunchMenuFeature.FEATURE_KEYWORDS,
            category = CommandCategory.LUNCH_MENU,
            subcategories = LunchMenuFeature.FEATURE_SUBCATEGORIES
        )
        
        self.command_mapping = {
            CommandSubcategory.LUNCH_YESTERDAY: lambda: self.interface.get_menu_for_weekday(today() - 1),
            CommandSubcategory.LUNCH_TODAY: lambda: self.interface.get_menu_for_weekday(today()),
            CommandSubcategory.LUNCH_TOMORROW: lambda: self.interface.get_menu_for_weekday(today() + 1),
            CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW: lambda: self.interface.get_menu_for_weekday(today() + 2),
            CommandSubcategory.LUNCH_FOR_WEEK: lambda: self.interface.get_menu_for_week()
        }

        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
        )        

        super().__init__(
            interface = Scraper(url = kwargs['url']),
            command_parser = self.command_parser, 
            command_mapping = self.command_mapping)

class JokeFeature(FeatureBase):

    FEATURE_KEYWORDS = (
        'skämt', 'meme',
        'skoja', 'skoj',
        'humor', 'roligt',
        'skämta'
    )

    FEATURE_SUBCATEGORIES = {
        'meme': CommandSubcategory.TELL_JOKE,
        'skämt': CommandSubcategory.TELL_JOKE,
        'skämta': CommandSubcategory.TELL_JOKE,
        'skoja': CommandSubcategory.TELL_JOKE,
        'skoj': CommandSubcategory.TELL_JOKE,
        'humor': CommandSubcategory.TELL_JOKE,
        'roligt': CommandSubcategory.TELL_JOKE
    }

    def __init__(self, *args, **kwargs):
        self.command_parser = JokeCommandFeatureCommandParser(
            keywords = JokeFeature.FEATURE_KEYWORDS,
            category = CommandCategory.TELL_JOKE,
            subcategories = JokeFeature.FEATURE_SUBCATEGORIES
        )

        self.command_mapping = {
            CommandSubcategory.TELL_JOKE: lambda: self.interface.get()
        }
        
        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
        )

        super().__init__(
            command_parser = self.command_parser,
            command_mapping = self.command_mapping,
            interface = RedditJoke(reddit_client = praw.Reddit(**kwargs))
                
        )

class ReminderFeature(FeatureBase):

    FEATURE_KEYWORDS = (
        'ihåg', 'memorera',
        'spara', 'påminna',
        'påminnelse', 'event',
        'events', 'påminnelser'
    )

    FEATURE_SUBCATEGORIES = {
        'ihåg': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'memorera': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'påminna': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'spara': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'påminna': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'event': CommandSubcategory.REMINDER_SHOW_EVENTS,
        'påminnelser': CommandSubcategory.REMINDER_SHOW_EVENTS,
        'aktiviteter': CommandSubcategory.REMINDER_SHOW_EVENTS
    }

    def __init__(self, *args, **kwargs):
        self.command_parser = ReminderFeatureCommandParser(
            keywords = ReminderFeature.FEATURE_KEYWORDS,
            category = CommandCategory.REMINDER,
            subcategories = ReminderFeature.FEATURE_SUBCATEGORIES
        )

        self.command_mapping = {
            CommandSubcategory.REMINDER_SHOW_EVENTS: lambda: self.interface.events,
            CommandSubcategory.REMINDER_REMEMBER_EVENT: self._remember_event,
        }

        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
            CommandPronoun.PERSONAL,
            CommandPronoun.POSSESSIVE
        )

        super().__init__(
            command_parser = self.command_parser,
            command_mapping = self.command_mapping,
            interface = Reminder()
        )

        self.command_parser.ignore_all(';')
        self.interactive_methods = (self._remember_event,)
    
    def _remember_event(self, message: list):

        invalid_format = 'Ogiltigt format, försök igen. Exempel:\n\n**rob, kan '\
                         'du komma ihåg; Nyår!, 2020-12-31-00:00\n\nDet är '\
                         'viktigt att ange ett semikolon och sedan separera med '\
                         'mellanslag och kommatecken. Datumformatet måste vara '\
                         'MÅNAD-DAG-TIMME:MINUT.'
        
        invalid_date = 'Du måste skapa en påminnelse minst 30 minuter i framtiden.'
        success = 'Det kommer en påminnelse en halvtimme innan :slight_smile:'
        
        message_as_str = ' '.join(message)

        try:
            task = message_as_str.split(';')[-1].split(',')
            body = task[0].strip()
            event_date = datetime.strptime(task[1].strip(), '%Y-%m-%d-%H:%M')
            if datetime.now() > event_date or ((event_date - datetime.now()).seconds / 60) < 30.0:
                return invalid_date
        except Exception as e:
            return invalid_format
        else:
            self.interface.add(Event(
                body = body, 
                date = event_date.date(), 
                time = time(hour = event_date.hour, minute = event_date.minute),
                alarm = timedelta(minutes = 30)))
        return success

class ScheduleFeature(FeatureBase):

    FEATURE_KEYWORDS = (
        'schema', 'schemat',
        'lektion', 'klassrum',
        'sal', 'lektioner',
        'lektion'
    )

    FEATURE_SUBCATEGORIES = {
        'nästa': CommandSubcategory.SCHEDULE_NEXT_LESSON,
        'klassrum': CommandSubcategory.SCHEDULE_NEXT_LESSON,
        'idag': CommandSubcategory.SCHEDULE_TODAYS_LESSONS,
        'imorgon': CommandSubcategory.SCHEDULE_TOMORROWS_LESSONS,
        'imorn': CommandSubcategory.SCHEDULE_TOMORROWS_LESSONS,
        'imorrn': CommandSubcategory.SCHEDULE_TOMORROWS_LESSONS,
        'schema': CommandSubcategory.SCHEDULE_CURRICULUM,
        'schemat': CommandSubcategory.SCHEDULE_CURRICULUM
    }
    
    def __init__(self, *args, **kwargs):
        self.command_parser = ScheduleFeatureCommandParser(
            keywords = ScheduleFeature.FEATURE_KEYWORDS,
            category = CommandCategory.SCHEDULE,
            subcategories = ScheduleFeature.FEATURE_SUBCATEGORIES
        )

        self.command_mapping = {
            CommandSubcategory.SCHEDULE_NEXT_LESSON: lambda: self._get_next_lesson(),
            CommandSubcategory.SCHEDULE_CURRICULUM: lambda: self._get_curriculum(),
            CommandSubcategory.SCHEDULE_TODAYS_LESSONS: lambda: self._get_todays_lessons()
        }

        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
        )

        super().__init__(
            command_parser = self.command_parser,
            command_mapping = self.command_mapping,
            interface = Schedule(**kwargs)
        )

    def _get_curriculum(self) -> str:
        '''
        Return string with the schedule for as long as forseeable
        with Schedule object. Take in to acount the 2000 character
        message limit in Discord. Append only until the length
        of the total string length of all elements combined are within
        0 - 2000 in length.s
        '''
        curriculum = []
        last_date = self.interface.curriculum[0].begin.date()
        allowed_length = 2000
        
        for index, event in enumerate(self.interface.curriculum):
            if event.begin.date() >= self.interface.today:
                begin = event.begin.adjusted_time.strftime('%H:%M')
                end = event.end.adjusted_time.strftime('%H:%M')
                location = event.location
                name = event.name
                date = event.begin.date()
                
                if date != last_date:
                    phrase = f'\n{name}\nKlassrum: {location}\nNär: {date} -- {begin}-{end}'
                else:
                    phrase = f'{name}\nKlassrum: {location}\nNär: {date} -- {begin}-{end}\n'
        
                if (allowed_length - len(phrase)) > 10:
                    curriculum.append(phrase)
                    allowed_length -= len(phrase)
                    last_date = event.begin.date()
                else:
                    break
        curriculum = '\n'.join(curriculum)        
        return f'**Här är schemat!** :slight_smile:\n\n{curriculum}'

    def _get_next_lesson(self) -> str:
        '''
        Return string with concatenated variable values to tell the
        human which is the next upcoming lesson.
        '''
        try:
            date = self.interface.next_lesson_date
            hour = self.interface.next_lesson_time
            classroom = self.interface.next_lesson_classroom
        except Exception as e:
            return e
        return f'Nästa lektion är i {classroom}, {date}, kl {hour} :slight_smile:'

    def _get_todays_lessons(self) -> str:
        '''
        Return concatenated response phrase with all lessons for 
        the current date. If none, return a message that explains
        no lessons for current date.
        '''
        if self.interface.todays_lessons:
            lessons = '\n'.join(self.interface.todays_lessons)
            return f'Här är schemat för dagen:\n{lessons}'
        return 'Det finns inga lektioner på schemat idag :sunglasses:'

class CommandProcessor:
    '''
    This object, while integrated to a front end
    works as a way to parse and understand what a
    human is asking for. An object containing the 
    representation of the interpretation of said
    sentence or word is returned of class 
    Interpretation.
    '''
    NO_IMPLEMENTATION = 'Det har mina utvecklare inte lagt in något svar för än :sad:'

    NO_SUBCATEGORY = (
        'Jag förstod nästan vad du menade, kan du uttrycka dig annorlunda?',
        'Hmm, jag har det på tungan. Kan du kontrollera stavningen?',
        'Nja... kan inte riktigt förstå vad du menar, säg igen?'
    )

    NO_RESPONSE = (
        'Jag har inget bra svar på det.',
        'Hm, vet inte vad du menar riktigt?',
        'Jag vet inte?',
        '?',
        'Vad menas? :thinking:'
    )

    def __init__(self, pronoun_lookup_table: PronounLookupTable):
        self._pronoun_lookup_table = pronoun_lookup_table
        self._feature_pronoun_mapping = dict()

    def process(self, message: str) -> CommandSubcategory:
        '''
        Part of the public interface. This method takes a 
        message in str format and splits it on space characters
        turning it in to a list. The message is decomposed by the
        private _interpret method for identifying pronouns, which
        funnel the message to the appropriate features in the 
        self._features collection. As an instance of Interpretation
        is returned from this call, it is passed on to the caller.
        '''
        message = message.lower().split(' ')
        interpretation = self._interpret(message)
        if interpretation:
            return interpretation
        return f'doh!'

    def _interpret(self, message: list) -> Interpretation:
        '''
        Identify the pronouns in the given message. Try to 
        match the pronouns aganst the mapped pronouns property
        for each featrure. If multiple features match the set of
        pronouns, the message is given to each feature for keyword
        matching. The feature that returns a match is given the
        message for further processing and ultimately returning
        the response.
        '''
        mapped_features = []
        any_in = lambda iter_a, iter_b: True if any([i in iter_a for i in iter_b]) else False
        found_pronouns = self._pronoun_lookup_table.lookup(message)
        
        for feature in self._features:
            if any_in(self._feature_pronoun_mapping[feature], found_pronouns):
                category = feature.command_parser.get_category(message)
                if category is None:
                    continue
                mapped_features.append(feature)

        if not len(mapped_features):
            return Interpretation(
                    command_pronouns = found_pronouns,
                    command_category = CommandCategory.UNIDENTIFIED,
                    original_message = (message,),
                    response = lambda: random.choice(CommandProcessor.NO_RESPONSE))
      
        for feature in mapped_features:
            try:
                subcategory = feature.command_parser.get_subcategory(message)
                return_callable = feature(message)
            except NotImplementedError as e:
                return Interpretation(
                        command_pronouns = found_pronouns,
                        command_category = feature.command_parser.category,
                        command_subcategory = subcategory,
                        response = lambda: CommandProcessor.NO_IMPLEMENTATION,
                        original_message = (message,),
                        error = e)
            else:
                if return_callable == CommandSubcategory.UNIDENTIFIED:
                    continue
                return Interpretation(
                        command_pronouns = found_pronouns,
                        command_category = feature.command_parser.category,
                        command_subcategory = subcategory,
                        response = return_callable,
                        original_message = (message,))

        return Interpretation(
                command_pronouns = found_pronouns,
                command_category = feature.command_parser.category,
                command_subcategory = CommandSubcategory.UNIDENTIFIED,
                response = lambda: random.choice(CommandProcessor.NO_SUBCATEGORY),
                original_message = (message,))

    @property
    def features(self) -> tuple:
        return self._features
    
    @features.setter
    def features(self, features: tuple):
        if not isinstance(features, tuple):
            raise TypeError(f'expected tuple, got {type(features)}')

        for feature in features:
            if not isinstance(feature, FeatureABC):
                raise TypeError(f'All features must inherit from FeatureABC, got {type(feature)}')
        
        for feature in features:
            self._feature_pronoun_mapping[feature] = feature.mapped_pronouns
        
        self._features = features

if __name__ == "__main__":

    import source.client as client
    environment_vars = client.load_environment()

    processor = CommandProcessor(pronoun_lookup_table = PronounLookupTable())
   
    processor.features = (
        ReminderFeature(),
        ScheduleFeature(url = environment_vars['TIMEEDIT_URL']),
        LunchMenuFeature(url = environment_vars['LUNCH_MENU_URL']),
        JokeFeature(client_id = environment_vars['REDDIT_CLIENT_ID'], 
                    client_secret = environment_vars['REDDIT_CLIENT_SECRET'],
                    user_agent = environment_vars['REDDIT_USER_AGENT']))

    while True:
        query = input('->')
        before = timer()
        a = processor.process(query)
        after = timer()
        
        print(f'Responded in {round(1000 * (after - before), 3)} milliseconds')

        if callable(a.response):
            print(f'\nINTERPRETATION:\n{a}\n\nEXECUTED METHOD: {a.response()}')
        else:
            print(f'was not callable: {a}')
        