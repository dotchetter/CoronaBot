import source.commandintegrator.framework as fw
import discord
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory
from source.commandintegrator.logger import logger
from source.coronafeatureclient import Client, ApiHandle

class CoronaSpreadFeatureCommandParser(fw.FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CoronaSpreadFeature(fw.FeatureBase):

    FEATURE_KEYWORDS = (
        'land',
        'många',
        'corona',
        'coronafall'
    )

    DataRecordTimeStamp_One = {'när': ('uppdaterad', 'uppdaterades')}
    DataRecordTimeStamp_Two = {'hur': ('gammal', 'data', 'datan')}

    TotalDeaths = {'totalt': ('dött', 'omkommit', 'döda')}
    TotalRecoveries = {'totalt': ('friska', 'tillfrisknat')}
    TotalCases = {'totalt': ('smittade', 'smittats', 'sjuka')}

    MostDeaths = {'flest': ('döda', 'dödsfall', 'omkommit', 'omkomna', 'dött')}
    MostRecoveries = {'flest': ('friska', 'tillfrisknat')}
    MostCases = {'flest': ('smittade', 'sjuka')}

    LeastDeaths = {'minst': ('döda', 'dödsfall', 'omkomna', 'omkommit', 'dött')}
    LeastRecoveris = {'minst': ('smittade', 'sjuka')}
    LeastCases = {'minst': ('friska', 'tillfrisknat')}

    InfectionsByQuery_One = {'har': ('smittats', 'sjuka')}
    InfectionsByQuery_Two = {'är': ('smittade', 'sjuka')}
    DeathsByQuery = {'har': ('dött', 'omkommit')}
    RecoveriesByQuery = {'har': ('friska', 'tillfrisknat')}


    FEATURE_SUBCATEGORIES = {
        str(DataRecordTimeStamp_One): CommandSubcategory.CORONA_DATA_TIMESTAMP,
        str(DataRecordTimeStamp_Two): CommandSubcategory.CORONA_DATA_TIMESTAMP,
        str(TotalDeaths): CommandSubcategory.CORONA_SPREAD_TOTAL_DEATHS,
        str(TotalRecoveries): CommandSubcategory.CORONA_SPREAD_TOTAL_RECOVERIES,
        str(TotalCases): CommandSubcategory.CORONA_SPREAD_TOTAL_INFECTIONS,
        str(MostDeaths): CommandSubcategory.CORONA_SPREAD_MOST_DEATHS,
        str(MostRecoveries): CommandSubcategory.CORONA_SPREAD_MOST_RECOVERIES,
        str(MostCases): CommandSubcategory.CORONA_SPREAD_MOST_INFECTIONS,
        str(LeastCases): CommandSubcategory.CORONA_SPREAD_LEAST_INFECTIONS,
        str(LeastDeaths): CommandSubcategory.CORONA_SPREAD_LEAST_DEATHS,
        str(LeastRecoveris): CommandSubcategory.CORONA_SPREAD_LEAST_RECOVERIES,
        str(InfectionsByQuery_One): CommandSubcategory.CORONA_INFECTIONS_BY_QUERY,
        str(InfectionsByQuery_Two): CommandSubcategory.CORONA_INFECTIONS_BY_QUERY,
        str(DeathsByQuery): CommandSubcategory.CORONA_DEATHS_BY_QUERY,
        str(RecoveriesByQuery): CommandSubcategory.CORONA_RECOVERIES_BY_QUERY
    }

    def __init__(self, *args, **kwargs):
        self.command_parser = CoronaSpreadFeatureCommandParser(
            category = CommandCategory.CORONA_SPREAD,
            keywords = CoronaSpreadFeature.FEATURE_KEYWORDS,
            subcategories = CoronaSpreadFeature.FEATURE_SUBCATEGORIES
        )


        self.callbacks = {
            CommandSubcategory.CORONA_SPREAD_TOTAL_DEATHS: lambda: self.get_total_deaths(),
            CommandSubcategory.CORONA_SPREAD_TOTAL_RECOVERIES: lambda: self.get_total_recoveries(),
            CommandSubcategory.CORONA_SPREAD_TOTAL_INFECTIONS: lambda: self.get_total_infections(),
            CommandSubcategory.CORONA_SPREAD_MOST_DEATHS: lambda: self.get_most_deaths(),
            CommandSubcategory.CORONA_SPREAD_MOST_RECOVERIES: lambda: self.get_most_recoveries(),
            CommandSubcategory.CORONA_SPREAD_MOST_INFECTIONS: lambda: self.get_most_infections(),
            CommandSubcategory.CORONA_SPREAD_LEAST_INFECTIONS: lambda: self.get_least_infections(),
            CommandSubcategory.CORONA_SPREAD_LEAST_DEATHS: lambda: self.get_least_deaths(),
            CommandSubcategory.CORONA_SPREAD_LEAST_RECOVERIES: lambda: self.get_least_recoveries(),
            CommandSubcategory.CORONA_DATA_TIMESTAMP: lambda: self.interface.get_data_timestamp(),
            CommandSubcategory.CORONA_INFECTIONS_BY_QUERY: self.get_cases_by_country,
            CommandSubcategory.CORONA_DEATHS_BY_QUERY: self.get_deaths_by_country,
            CommandSubcategory.CORONA_RECOVERIES_BY_QUERY: self.get_recoveries_by_country
        }

        self.interactive_methods = (
            self.get_cases_by_country,
            self.get_recoveries_by_country,
            self.get_deaths_by_country
        )

        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
        )

        api_handle = ApiHandle(uri = kwargs['uri'])
        api_handle.add_header('x-rapidapi-host', kwargs['corona_rapidapi_host'])
        api_handle.add_header('x-rapidapi-key', kwargs['corona_rapidapi_key'])

        super().__init__(
            command_parser = self.command_parser,
            callbacks = self.callbacks,
            interface = Client(api_handle),
            interactive_methods = self.interactive_methods
        )

    @logger
    def get_total_deaths(self):
        response = self.interface.get_total_deaths()
        #return f'Totalt har {response} omkommit globalt'
        return self.interface.get_raw_data()
    
    @logger
    def get_total_recoveries(self):
        response = self.interface.get_total_recoveries()
        return f'Totalt har {response} tillfrisknat globalt'
    
    @logger
    def get_total_infections(self):
        response = self.interface.get_total_infections()
        return f'Totalt har {response} insjuknat globalt'
    
    @logger
    def get_most_deaths(self):
        response = self.interface.get_deaths()
        return f'Flest har omkommit i {response}'
    
    @logger
    def get_most_recoveries(self):
        response = self.interface.get_recoveries()
        return f'Flest har tillfrisknat i {response}'
    
    @logger
    def get_most_infections(self):
        response = self.interface.get_infections()
        return f'Totalt har {response} insjuknat globalt'
    
    @logger
    def get_least_infections(self):
        response = self.interface.get_infections(sort_by_highest = False)
        return f'Minst antal insjuknade har {response}'
    
    @logger
    def get_least_deaths(self):
        response = self.interface.get_deaths(sort_by_highest = False)
        return f'Minst antal dödsfall har {response}'
   
    @logger
    def get_least_recoveries(self):
        response = self.interface.get_recoveries(sort_by_highest = False)
        return f'Minst tillfrisknade: {response}'

    @logger
    def get_cases_by_country(self, message: discord.Message) -> str:
        """
        Get cases by country.
        :param message:
            original message from Discord
        :returns:
            str
        """
        try:
            country = message.content[-1].strip(fw.FeatureCommandParserBase.IGNORED_CHARS)
            response = self.interface.get_by_query(query = 'cases', country_name = country)
            return f'{response} har smittats av corona i {country}'
        except Exception as e:
            return f'Ingen data: {e}'

    @logger
    def get_recoveries_by_country(self, message: discord.Message) -> str:
        """
        Get recoveries by country.
        :param message:
            original message from Discord
        :returns:
            str
        """
        try:
            country = message.content[-1].strip(fw.FeatureCommandParserBase.IGNORED_CHARS)
            response = self.interface.get_by_query(query = 'total_recovered', country_name = country)
            return f'{response} har tillfrisknat i corona i {country}'
        except Exception as e:
            return f'Ingen data: {e}'

    @logger
    def get_deaths_by_country(self, message: discord.Message) -> str:
        """
        Get deaths by country.
        :param message:
            original message from Discord
        :returns:
            str
        """
        try:
            country = message.content[-1].strip(fw.FeatureCommandParserBase.IGNORED_CHARS)
            response = self.interface.get_by_query(query = 'deaths', country_name = country)
            return f'{response} har omkommit i corona i {country}'
        except Exception as e:
            return f'Ingen data: {e}'