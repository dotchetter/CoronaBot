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

class MetaFileError(Exception):
	pass

class InvalidCalendarUrl(Exception):
	pass

class TimezoneAdjustmentError(Exception):
	pass