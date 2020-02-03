import source.commandintegrator.framework as fw
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory
from source.scraper import Scraper
from datetime import datetime, timedelta


class LunchMenuFeatureCommandParser(fw.FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_subcategory(self, message: list) -> CommandSubcategory:
        for word in message:
            word = word.strip(fw.FeatureCommandParserABC.IGNORED_CHARS)
            if word in self._subcategories:
                return self._subcategories[word]
        return CommandSubcategory.LUNCH_TODAY


class LunchMenuFeature(fw.FeatureBase):

    FEATURE_KEYWORDS = (
        'lunch', 'mat',
        'käk', 'krubb',
        'föda', 'tugg',
        'matsedel'
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
        
        self.command_mapping = {
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
            command_mapping = self.command_mapping)

    def menu_for_week(self) -> str:
        '''
        Return the entire week's menu with one empty line
        separating the lists of entries.
        '''
        days = ('**Måndag**', '**Tisdag**', '**Onsdag**', '**Torsdag**', '**Fredag**')
        menu_for_week = self.interface.get_menu_for_week()
        
        for index, day in enumerate(menu_for_week):
            day.insert(0, days[index])
            if not len(day):
                day.append('Meny inte tillgänglig.')
            day.append('\n')
        return f'Här är veckans meny :slight_smile:\n{menu_for_week}'
    
    def menu_for_weekday_phrase(self, weekday: datetime, when: CommandSubcategory) -> str:
        '''
        Return a user-friendly variant of the content
        retreived by the interface object's methods,
        for display on front end. Expect a weekday 
        alias, meaning today, tomorrow etc for describing
        the day for which the menu concerns.
        '''

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
        return f'Detta server{tense} {tempus[when]}! {menu}'