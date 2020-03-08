import argparse
import random
import json
import discord
import traceback
from itertools import zip_longest
from ast import literal_eval
from pprint import pprint
from os import system
from datetime import datetime, timedelta, time
from enum import Enum, auto
from dataclasses import dataclass
from abc import ABC, abstractmethod
from timeit import default_timer as timer
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory

"""
Details:
    2019-12-23

    CommandIntegrator framework source file

      --- ABSOLUTELY DO NOT MODIFY THIS FILE ---

    Any changes or suggestions for improvement to this
    framework should be appealed by cloning this file
    and sending a pull request to the repository with 
    changes in place, in the cloned file. 

Module details:
    
    This file contains abstract and base classes for 
    the framework called CommandIntegrator. 

    In order for a developer to integrate their software
    with a way to bind certain actions and methods in their
    code, the developer needs a way to follow a set of routines
    that guarantees a seamless integration with the front end
    of the application. This framework provides base classes
    to inherit from with a strict set of rules and methods
    already provided to make it easier for the application 
    to scale, as well as letting developers easily integrate
    their software to the front end with their own interfaces.

    To read instructions and see examples how to use this 
    framework with your application - please read the full
    documentation.

"""



class PronounLookupTable:
    """
    Provide a grammatic framework that 
    returns a tuple of matches for certain
    grammatic classes of words found in a given
    sentence. 
    """

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

    def __repr__(self):
        return f'PronounLookupTable({self._lookup_table})'

    def lookup(self, message: list) -> tuple:
        """
        Split a given string by space if present, to iterate
        over a sentence of words. Returns a tuple with enum
        instances representing the pronouns that make up the
        composition of the string received. If none is found,
        a tuple with a single CommandPronoun.UNIDENTIFIED is 
        returned.
        """
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
    """
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
    """
    command_pronouns: tuple(CommandPronoun) = ()
    command_category: CommandCategory = None,
    command_subcategory: CommandSubcategory = None,
    original_message: tuple = ()
    response: callable = None
    error: Exception = None


class FeatureCommandParserABC(ABC):
    """
    Describe a data structure that binds certain
    keywords to a certain feature. As the feature
    stack grows, this class is used as a template
    for base classes that work with decomposing 
    a message string, trying to understand its context
    and intent.
    """
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
    def get_category(self, message: discord.Message) -> CommandCategory:
        """
        Iterate over the words in received message, and 
        see if any of the words line up with the keywords
        provided for an instance of this class. If a match
        is found, the CommandCategory of the instance should
        return, otherwise None.
        """
        return
    
    @abstractmethod
    def get_subcategory(self, message: discord.Message) -> CommandSubcategory:
        """
        Returns a ResponseOption enum type that indicates more 
        precisely which method for a feature that the command 
        is matched against. This method should be overloaded if 
        a different return behaviour in a no-match-found scenario
        is desired.
        """
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

    def __repr__(self):
        return f'FeatureCommandParser({self.category})'

    def __contains__(self, word: str) -> bool:
        return word in self._keywords

    def ignore_all(self, char: str):
        self.ignored_chars[char] = ''

    def get_category(self, message: discord.Message) -> CommandCategory:
        for key in self.ignored_chars:
            message.content = [word.replace(key, self._ignored_chars[key]) for word in message.content]

        for word in message.content:
            if word.strip(FeatureCommandParserBase.IGNORED_CHARS) in self:
                return self._category
        return None
    
    def get_subcategory(self, message: discord.Message) -> CommandSubcategory:

        strip_chars = lambda string: string.strip(FeatureCommandParserBase.IGNORED_CHARS)
        complex_subcategories = []
        simple_subcategories = []
        
        for key in self._subcategories.keys():
            try:
                complex_subcategories.append(literal_eval(key))
            except:
                simple_subcategories.append(key)

        for subcategory in complex_subcategories:
            for word in message.content:
                word = strip_chars(word)
                try:
                    subset = subcategory[word]
                except KeyError:
                    pass
                else:
                    if [strip_chars(i) for i in message.content if strip_chars(i) in subset]:
                        return self._subcategories[str(subcategory)]
    
        for word in message.content:
            word = strip_chars(word)
            if word in simple_subcategories:
                return self._subcategories[word]
        return CommandSubcategory.UNIDENTIFIED

    @property
    def category(self):
        return self._category
    
    @category.setter
    def category(self, category: CommandCategory):
        if not isinstance(category, Enum):
            raise TypeError(f'category must be CommandCategory enum, got {type(category)}')
        self._category = category

    @property
    def keywords(self) -> tuple:
        return self._keywords
    
    @keywords.setter
    def keywords(self, keywords: tuple):
        if not isinstance(keywords, tuple):
            raise TypeError(f'keywords must be tuple, got {type(keywords)}')
        self._keywords = keywords

    @property
    def subcategories(self) -> dict:
        return self._subcategories
    
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
    

class FeatureABC(ABC):
    """ 
    Represent the template for a complete and 
    ready-to-use feature. 
    """
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
    def callbacks(self) -> dict:
        return
    
    @callbacks.setter
    @abstractmethod
    def callbacks(self, callbacks: dict):
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
    """
    Base class for features coupled to the chatbot. 
    Use this class as a base class to inherit from when
    connecting your feature's interface to the bot.
    """

    def __init__(self, *args, **kwargs):
        self.interactive_methods = tuple()
        super().__init__(*args, **kwargs)

    def __call__(self, message: discord.Message) -> callable:
        try:
            command_subcategory = self._command_parser.get_subcategory(message)
            if command_subcategory == CommandSubcategory.UNIDENTIFIED:
                return CommandSubcategory.UNIDENTIFIED

            if self.callbacks[command_subcategory] in self.interactive_methods:
                method = self.callbacks[command_subcategory]
                return lambda message = message: method(message)
            return self.callbacks[command_subcategory]
        except KeyError:
            raise NotImplementedError(f'no mapped function call for {command_subcategory} in self')

    def __repr__(self):
        return f'Feature({self.command_parser.category})'
    
    @property
    def mapped_pronouns(self) -> tuple:
        return self._mapped_pronouns

    @mapped_pronouns.setter
    def mapped_pronouns(self, pronouns: tuple = ()):
        if not isinstance(pronouns, tuple):
            raise TypeError(f'pronouns must be enclosed in a tuple, got {type(pronouns)}')
                
        self._mapped_pronouns = list(pronouns)
        self._mapped_pronouns.insert(0, CommandPronoun.UNIDENTIFIED)
        self._mapped_pronouns = tuple(self._mapped_pronouns)

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
    def callbacks(self) -> dict:
        return self._callbacks
    
    @callbacks.setter
    def callbacks(self, callbacks: dict):
        if not isinstance(callbacks, dict):
            raise TypeError(f'command_parser must be dict, got {type(callbacks)}')
        
        for key in callbacks:
            if not isinstance(key, Enum):
                raise TypeError(f'key must be CommandSubcategory Enum, got {type(key)}')
            elif not callable(callbacks[key]):
                raise TypeError(f'"{callbacks[key]}" is not callable.')
        self._callbacks = callbacks

    @property
    def interactive_methods(self) -> tuple:
        return self._interactive_methods
    
    @interactive_methods.setter
    def interactive_methods(self, arg: tuple):
        if not isinstance(arg, tuple):
            raise TypeError(f'interactive methods must be enclosed in tuple, got {type(arg)}')
        for i in arg:
            if not callable(i):
                raise TypeError(f'Warning: interactive method not callable: {i}')
        self._interactive_methods = arg


class CommandProcessor:
    """
    This object, while integrated to a front end
    works as a way to parse and understand what a
    human is asking for. An object containing the 
    representation of the interpretation of said
    sentence or word is returned of class 
    Interpretation.
    """

    def __init__(self, pronoun_lookup_table: PronounLookupTable, default_responses: dict):
        self._pronoun_lookup_table = pronoun_lookup_table
        self._feature_pronoun_mapping = dict()
        self._default_responses = default_responses

    @property
    def features(self) -> tuple:
        return self._features
    
    @features.setter
    def features(self, features: tuple):
        if not isinstance(features, tuple):
            raise TypeError(f'expected tuple, got {type(features)}')
        
        for feature in features:
            self._feature_pronoun_mapping[feature] = feature.mapped_pronouns
        self._features = features

    def process(self, message: discord.Message) -> CommandSubcategory:
        """
        Part of the public interface. This method takes a discord.Message
        object  and splits the .content property on space characters
        turning it in to a list. The message is decomposed by the
        private _interpret method for identifying pronouns, which
        funnel the message to the appropriate features in the 
        self._features collection. As an instance of Interpretation
        is returned from this call, it is passed on to the caller.
        """
        message.content = message.content.lower().split(' ')
        try:
            return self._interpret(message)
        except Exception as e:
            return Interpretation(error = traceback.format_exc(),
                        response = lambda: f'CommandProcessor: Internal error',
                        original_message = message)
   
    def _interpret(self, message: discord.Message) -> Interpretation:
        """
        Identify the pronouns in the given message. Try to 
        match the pronouns aganst the mapped pronouns property
        for each featrure. If multiple features match the set of
        pronouns, the message is given to each feature for keyword
        matching. The feature that returns a match is given the
        message for further processing and ultimately returning
        the response.
        """
        mapped_features = list()
        found_pronouns = self._pronoun_lookup_table.lookup(message.content)
        
        for feature in self._features:
            if bool(set(self._feature_pronoun_mapping[feature]).intersection(found_pronouns)):
                category = feature.command_parser.get_category(message)                
                if category is not None: mapped_features.append(feature)

        if not mapped_features:
            return Interpretation(command_pronouns = found_pronouns,
                command_category = CommandCategory.UNIDENTIFIED,
                original_message = (message,),
                response = lambda: random.choice(self._default_responses['NoResponse']))

        for feature in mapped_features:
            try:
                subcategory = feature.command_parser.get_subcategory(message)
                return_callable = feature(message)
            except NotImplementedError as e:
                return Interpretation(command_pronouns = found_pronouns,
                            command_category = feature.command_parser.category,
                            command_subcategory = subcategory,
                            response = lambda: random.choice(self._default_responses['NoImplementation']),
                            original_message = (message,),
                            error = e)
            else:
                if return_callable == CommandSubcategory.UNIDENTIFIED:
                    continue
                return Interpretation(command_pronouns = found_pronouns,
                            command_category = feature.command_parser.category,
                            command_subcategory = subcategory,
                            response = return_callable,
                            original_message = (message,))

        return Interpretation(command_pronouns = found_pronouns,
                    command_category = feature.command_parser.category,
                    command_subcategory = CommandSubcategory.UNIDENTIFIED,
                    response = lambda: random.choice(self._default_responses['NoSubCategory']),
                    original_message = (message,))


if __name__ == "__main__":

    enviromnent_strings = [
        'DISCORD_GUILD',
        'TIMEEDIT_URL',
        'LUNCH_MENU_URL',
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT',
        'GOOGLE_API_KEY',
        'GOOGLE_CSE_ID',
        'DISCORD_TOKEN',
        'CORONA_API_URI',
        'CORONA_API_RAPIDAPI_HOST',
        'CORONA_API_RAPIDAPI_KEY'
    ]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-testmode', action = 'store_true')
    args = arg_parser.parse_args()

    import source.client as client
    from source.features.LunchMenuFeature import LunchMenuFeature
    from source.features.RedditJokeFeature import RedditJokeFeature
    from source.features.ScheduleFeature import ScheduleFeature
    from source.features.CoronaSpreadFeature import CoronaSpreadFeature

    with open('commandintegrator.settings.json', 'r', encoding = 'utf-8') as f:
        default_responses = json.loads(f.read())['default_responses']

    environment_vars = client.load_environment(enviromnent_strings)
    
    processor = CommandProcessor(
        pronoun_lookup_table = PronounLookupTable(), 
        default_responses = default_responses
    )
    
    processor.features = (
        
        ScheduleFeature(url = environment_vars['TIMEEDIT_URL']),
        
        CoronaSpreadFeature(
            CORONA_API_URI = environment_vars['CORONA_API_URI'],
            CORONA_API_RAPIDAPI_HOST = environment_vars['CORONA_API_RAPIDAPI_HOST'],
            CORONA_API_RAPIDAPI_KEY = environment_vars['CORONA_API_RAPIDAPI_KEY'],
            translation_file_path = 'C:\\users\\admin\\git\\robbottherobot\\source\\country_eng_swe_translations.json'
        ),

        LunchMenuFeature(
            url = environment_vars['LUNCH_MENU_URL']),
            RedditJokeFeature(
                client_id = environment_vars['REDDIT_CLIENT_ID'], 
                client_secret = environment_vars['REDDIT_CLIENT_SECRET'],
                user_agent = environment_vars['REDDIT_USER_AGENT']
            )
        )

    # --- FOR TESTING THE COMMANDPROCESSOR CLASS --- 

    mock_message = discord.Message

    if args.testmode:
        while True:
            mock_message.content = input('->')

            if not len(mock_message.content):
                continue

            before = timer()
            a = processor.process(mock_message)
            after = timer()

            print(f'Responded in {round(1000 * (after - before), 3)} milliseconds')

            if callable(a.response):
                print(f'\nINTERPRETATION:\n{a}\n\nEXECUTED METHOD: {a.response()}')
                if a.error:
                    print('Errors occured, see caught traceback below.')
                    pprint(a.error)
            else:
                print(f'was not callable: {a}')