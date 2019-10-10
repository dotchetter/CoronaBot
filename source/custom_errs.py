'''
Details:
    2019-09-25

Module details:
    Custom error classes

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class schedule and then
    share the current classroom for the day or week in the chat
    with a chatbot. 
'''

class MetaFileError(Exception):
    pass

class InvalidCalendarUrl(Exception):
    pass

class TimezoneAdjustmentError(Exception):
    pass

class EnvironmentVariableError(Exception):
	pass