from enum import Enum, auto

class CommandSubcategory(Enum):
    '''
    Constant enumerators for matching keywords against when
    deciding which response to give a given command.
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
    PERSONAL = auto()
    CORONA_SPREAD = auto()
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
