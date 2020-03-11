from enum import Enum, auto

class CommandSubcategory(Enum):
    """
    Constant enumerators for matching keywords against when
    deciding which response to give a given command.
    """
    SCHEDULE_NEXT_LESSON = auto()
    SCHEDULE_TODAYS_LESSONS = auto()
    SCHEDULE_TOMORROWS_LESSONS = auto()
    SCHEDULE_CURRICULUM = auto()
    
    REMINDER_REMEMBER_EVENT = auto()
    REMINDER_SHOW_EVENTS = auto()
    
    TELL_JOKE = auto()

    LUNCH_TODAY = auto()
    LUNCH_YESTERDAY = auto()
    LUNCH_TOMORROW = auto()
    LUNCH_DAY_AFTER_TOMORROW = auto()
    LUNCH_FOR_WEEK = auto()

    CORONA_SPREAD_TOTAL_DEATHS = auto()
    CORONA_SPREAD_TOTAL_RECOVERIES = auto()
    CORONA_SPREAD_TOTAL_INFECTIONS = auto()
    CORONA_SPREAD_MOST_DEATHS = auto()
    CORONA_SPREAD_MOST_RECOVERIES = auto()
    CORONA_SPREAD_MOST_INFECTIONS = auto()
    CORONA_SPREAD_LEAST_INFECTIONS = auto()
    CORONA_SPREAD_LEAST_DEATHS = auto()
    CORONA_SPREAD_LEAST_RECOVERIES = auto()
    CORONA_INFECTIONS_BY_QUERY = auto()
    CORONA_DEATHS_BY_QUERY = auto()
    CORONA_RECOVERIES_BY_QUERY = auto()
    CORONA_DATA_TIMESTAMP = auto()
    CORONA_NEW_CASES_BY_QUERY = auto()

    RANKING_DOWN = auto()
    RANKING_UP = auto()
    RANKING_FOR_MEMBER = auto()
    RANKING_FOR_ALL = auto()

    UNIDENTIFIED = auto()

class CommandCategory(Enum):
    """
    Various commands that are supported. 
    """
    LUNCH_MENU = auto()
    TELL_JOKE = auto()
    SCHEDULE = auto()
    REMINDER = auto()
    PERSONAL = auto()
    CORONA_SPREAD = auto()
    RANKING = auto()
    UNIDENTIFIED = auto()

class CommandPronoun(Enum):
    """
    Identifiable pronouns in recieved commands.
    __lt__ is implemented in order for a sorted
    set of instances to be returned.
    """
    INTERROGATIVE = auto()
    PERSONAL = auto()
    POSSESSIVE = auto()
    UNIDENTIFIED = auto()

    def __lt__(self, other):
        return self.value < other.value
