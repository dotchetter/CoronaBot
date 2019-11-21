from enum import Enum, auto

'''
Details:
    2019-11-19

Module details:
    ResponseOptions
    Enumerate the different responses that the bot 
    uses to point to a designated response method.

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class schedule and then
    share the current classroom for the day or week in the chat
    with
'''

class ResponseOptions(Enum):
    '''
    Constant enumerators for matching keywords against when
    deciding which response to give a given command to the bot.
    '''
    NEXT_LESSON = auto()
    TODAYS_LESSONS = auto()
    SCHEDULE = auto()
    SHOW_BOT_COMMANDS = auto()
    MEANING_OF_LIFE = auto()
    REMEMBER_EVENT = auto()
    SHOW_EVENTS = auto()
    ADJECTIVE = auto()
    JOKE = auto()
