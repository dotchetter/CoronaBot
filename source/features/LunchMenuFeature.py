import os
import discord
import source.commandintegrator as fw
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory
from source.commandintegrator.logger import logger
from source.scraper import Scraper
from datetime import datetime, timedelta


class LunchMenuFeatureCommandParser(fw.FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_subcategory(self, message: discord.Message) -> CommandSubcategory:
        for word in message.content:
            stripped_word = word.strip(fw.FeatureCommandParserBase.IGNORED_CHARS) 
            if stripped_word in self._subcategories:
                return self._subcategories[stripped_word]
        return CommandSubcategory.LUNCH_TODAY
    
class LunchMenuFeature(fw.FeatureBase):

    FEATURE_KEYWORDS = (
        'lunch', 'mat',
        'käk', 'krubb',
        'föda', 'tugg',
        'matsedel', 'meny'
    )

    FEATURE_SUBCATEGORIES = {
        'igår': CommandSubcategory.LUNCH_YESTERDAY,
        'idag': CommandSubcategory.LUNCH_TODAY,
        'imor': CommandSubcategory.LUNCH_TOMORROW,
        'imorn': CommandSubcategory.LUNCH_TOMORROW,
        'imorgon': CommandSubcategory.LUNCH_TOMORROW,
        'imoron': CommandSubcategory.LUNCH_TOMORROW,
        'imorron': CommandSubcategory.LUNCH_TOMORROW,
        'imorrn': CommandSubcategory.LUNCH_TOMORROW,
        'övermorgon': CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW,
        'övermorn': CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW,
        'övermorrn': CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW,
        'vecka': CommandSubcategory.LUNCH_FOR_WEEK,
        'veckan': CommandSubcategory.LUNCH_FOR_WEEK,
        'veckans': CommandSubcategory.LUNCH_FOR_WEEK
    }

    def __init__(self, **kwargs):
        
        self.command_parser = LunchMenuFeatureCommandParser(
            category = CommandCategory.LUNCH_MENU,
            keywords = LunchMenuFeature.FEATURE_KEYWORDS,
            subcategories = LunchMenuFeature.FEATURE_SUBCATEGORIES
        )
        
        self.callbacks = {
            CommandSubcategory.LUNCH_YESTERDAY: lambda: 
                self.menu_for_weekday_phrase(
                    weekday = datetime.now() - timedelta(days = 1),
                    when = CommandSubcategory.LUNCH_YESTERDAY),
            
            CommandSubcategory.LUNCH_TODAY: lambda: 
                self.menu_for_weekday_phrase(
                    weekday = datetime.now(),
                    when = CommandSubcategory.LUNCH_TODAY),
            
            CommandSubcategory.LUNCH_TOMORROW: lambda: 
                self.menu_for_weekday_phrase(
                    weekday = datetime.now() + timedelta(days = 1),
                    when = CommandSubcategory.LUNCH_TOMORROW),
            
            CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW: lambda: 
                self.menu_for_weekday_phrase(
                    weekday = datetime.now() + timedelta(days = 2),
                    when = CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW),
            
            CommandSubcategory.LUNCH_FOR_WEEK: lambda: 
                self.menu_for_week()
        }

        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
        )        

        super().__init__(
            interface = Scraper(url = kwargs['url']),
            command_parser = self.command_parser, 
            callbacks = self.callbacks)

    @logger
    def menu_for_week(self) -> str:
        """
        Return the entire week's menu with one empty line
        separating the lists of entries.
        """
        days = ('**Måndag**', '**Tisdag**', '**Onsdag**', '**Torsdag**', '**Fredag**')
        menu_for_week = self.interface.get_menu_for_week()
        output = str()
        
        for index, day in enumerate(menu_for_week):
            day.insert(0, days[index])
            if not len(day):
                day.append('Meny inte tillgänglig.')
            day.append(os.linesep)
        
        for day in menu_for_week:
            output += os.linesep.join(day)

        return f'Här är veckans meny :slight_smile:{os.linesep}{os.linesep}{output}'
    
    @logger
    def menu_for_weekday_phrase(self, weekday: datetime, when: CommandSubcategory) -> str:
        """
        Return a user-friendly variant of the content
        retreived by the interface object's methods,
        for display on front end. The method .purge_cache
        will be called if the menu object is 5 days or older
        upon query, to prevent displaying old data from previous
        week.
        :param weekday:
            datetime for the day that the query concerns
        :when:
            CommandSubcategory Enum for matching tempus agains
        :returns:
            string
        """
        if self.interface.cache and (datetime.now().date() - self.interface.cache.creation_date).days >= 5:
            self.interface.purge_cache()

        tempus = {
            CommandSubcategory.LUNCH_YESTERDAY: 'igår',
            CommandSubcategory.LUNCH_TODAY: 'idag',
            CommandSubcategory.LUNCH_TOMORROW: 'imorgon',
            CommandSubcategory.LUNCH_DAY_AFTER_TOMORROW: 'i övermorgon'
        }

        if when == CommandSubcategory.LUNCH_YESTERDAY:
            tense = 'ades'
        else:
            tense = 'as'

        menu = self.interface.get_menu_for_weekday(weekday.weekday())
        if menu is None:
            return f'Jag ser inget på menyn för {tempus[when]}.'
        return f'Detta server{tense} {tempus[when]}!{os.linesep}{os.linesep}{os.linesep.join(menu)}'