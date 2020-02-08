import discord
import source.commandintegrator.framework as fw
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory
from source.reminder import Reminder
from source.event import Event

class ReminderFeatureCommandParser(fw.FeatureCommandParserBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReminderFeature(fw.FeatureBase):

    FEATURE_KEYWORDS = (
        'ihåg', 'memorera',
        'spara', 'påminna',
        'påminnelse', 'event',
        'events', 'påminnelser'
    )

    FEATURE_SUBCATEGORIES = {
        'ihåg': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'memorera': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'påminna': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'spara': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'påminna': CommandSubcategory.REMINDER_REMEMBER_EVENT,
        'event': CommandSubcategory.REMINDER_SHOW_EVENTS,
        'påminnelser': CommandSubcategory.REMINDER_SHOW_EVENTS,
        'påminnelse': CommandSubcategory.REMINDER_SHOW_EVENTS,
        'aktiviteter': CommandSubcategory.REMINDER_SHOW_EVENTS,
    }

    def __init__(self, *args, **kwargs):
        self.command_parser = ReminderFeatureCommandParser(
            category = CommandCategory.REMINDER,
            keywords = ReminderFeature.FEATURE_KEYWORDS,
            subcategories = ReminderFeature.FEATURE_SUBCATEGORIES
        )

        self.command_mapping = {
            CommandSubcategory.REMINDER_SHOW_EVENTS: lambda: self.interface.events,
            CommandSubcategory.REMINDER_REMEMBER_EVENT: self._remember_event,
        }

        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
            CommandPronoun.PERSONAL,
            CommandPronoun.POSSESSIVE
        )

        super().__init__(
            command_parser = self.command_parser,
            command_mapping = self.command_mapping,
            interface = Reminder()
        )

        self.command_parser.ignore_all(';')
        self.interactive_methods = (self._remember_event,)
    
    def _remember_event(self, message: discord.Message):

        invalid_format = 'Ogiltigt format, försök igen. Exempel:\n\n**rob, kan '\
                         'du komma ihåg; Nyår!, 2020-12-31-00:00\n\nDet är '\
                         'viktigt att ange ett semikolon och sedan separera med '\
                         'mellanslag och kommatecken. Datumformatet måste vara '\
                         'MÅNAD-DAG-TIMME:MINUT.'
        
        invalid_date = 'Du måste skapa en påminnelse minst 30 minuter i framtiden.'
        success = 'Det kommer en påminnelse en halvtimme innan :slight_smile:'
        
        message_as_str = ' '.join(message.content)

        try:
            task = message_as_str.split(';')[-1].split(',')
            body = task[0].strip()
            event_date = datetime.strptime(task[1].strip(), '%Y-%m-%d-%H:%M')
            if datetime.now() > event_date or ((event_date - datetime.now()).seconds / 60) < 30.0:
                return invalid_date
        except Exception as e:
            return invalid_format
        else:
            self.interface.add(Event(
                body = body, 
                date = event_date.date(), 
                time = time(hour = event_date.hour, minute = event_date.minute),
                alarm = timedelta(minutes = 30)))
        return success