from dataclasses import dataclass
from datetime import datetime

'''
Details:
    2019-11-19

Module details:
    UnrecognizedCommand
    Represent an unregocnized command from a user.
    Used for data metrics and logging.

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class schedule and then
    share the current classroom for the day or week in the chat
    with a chatbot. 
'''

@dataclass
class UnrecognizedCommand:
    '''
    Represent a message recieved in chat that the bot
    was unable to handle. Store message content, author
    and when it was recieved.
    '''
    command: str
    author: str
    timestamp: None

    @property
    def timestamp(self):
        return self.timestamp

    @timestamp.setter
    def timestamp(self, value):
        if isinstance(value, datetime):
            self.timestamp = value.isoformat()