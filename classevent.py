from dataclasses import dataclass
from datetime import datetime
'''
Details:
    2019-09-25

Module details:
    Application backend logic; Event describing class

Synposis:
    Supply a discord chatbot with intelligence and features.
    The goal is to subscribe to the class schedule and then
    share the current classroom for the day or week in the chat
    with a chatbot. 
'''

@dataclass
class ClassEvent:
	where: str
	when: datetime
	body: str