import discord
import source.commandintegrator.framework as fw
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory
from source.timeeditschedule import Schedule
from source.commandintegrator.logger import logger


class ScheduleFeatureCommandParser(fw.FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ScheduleFeature(fw.FeatureBase):

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
            category = CommandCategory.SCHEDULE,
            keywords = ScheduleFeature.FEATURE_KEYWORDS,
            subcategories = ScheduleFeature.FEATURE_SUBCATEGORIES
        )

        self.callbacks = {
            CommandSubcategory.SCHEDULE_NEXT_LESSON: lambda: self._get_next_lesson(),
            CommandSubcategory.SCHEDULE_CURRICULUM: lambda: self._get_curriculum(),
            CommandSubcategory.SCHEDULE_TODAYS_LESSONS: lambda: self._get_todays_lessons(),
            CommandSubcategory.SCHEDULE_TOMORROWS_LESSONS: lambda: self._get_tomorrows_lessons()
        }

        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
        )

        super().__init__(
            command_parser = self.command_parser,
            callbacks = self.callbacks,
            interface = Schedule(**kwargs)
        )

    @logger
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

    @logger
    def get_todays_lessons(self) -> str:
        '''
        Return concatenated response phrase with all lessons for 
        the current date. If none, return a message that explains
        no lessons for current date.
        '''
        if self.interface.todays_lessons:
            lessons = '\n'.join(self.interface.todays_lessons)
            return f'Här är schemat för dagen:\n{lessons}'
        return 'Det finns inga lektioner på schemat idag :sunglasses:'

    @logger
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

    @logger
    def _get_tomorrows_lessons(self) -> str:
        '''
        Returns the lessons in schedule for the day 
        after parsed date upon method execution, if any
        are present, otherwise a message delivering the
        absence of lessons.
        '''

        if self.interface.tomorrows_lessons:
            for event in self.interface.tomorrows_lessons:
                name = event.name.split(',')[-1].strip()
                event_start = event.begin.adjusted_time.strftime('%H:%M')
                event_end = event.end.adjusted_time.strftime('%H:%M')
                output.append(f'{name}, {event_start} - {event_end} i {event.location}')
            return output
        return 'Jag ser inga lektioner på schemat imorgon.'