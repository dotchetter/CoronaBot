import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

"""
This module contains the interface class used by the 
Corona Spread feature, making an API request to the
Corona Monitor API, which is hosted at Rapid Api and
can be found here:

https://rapidapi.com/astsiatsko/api/coronavirus-monitor/
"""


class ApiHandle:
	"""
	Call api and parse output to JSON. Returns cache 
	unless the data over 2 hours old by default as to not 
	overload the api service. The object calls the api upon
	instantiation, and will automatically cache the response.
	"""

	def __init__(self, uri: str, standby_hours = 2):
		self.uri: str = uri
		self._last_api_call: datetime = None
		self._wait_time = (60 * 60) * standby_hours
		self._cached_response: dict = None
		self._request = Request(self.uri)

	@property
	def uri(self) -> str:
		return self._uri
	
	@uri.setter
	def uri(self, uri: str) -> None:
		if uri.startswith('https'):
			self._uri = uri
		else:
			raise AttributeError('Got "http", expected "https"')

	def add_header(self, key: str, value: str) -> None:
		"""
		Act as an interface for the Request instance's
		add_header method.
		"""
		self._request.add_header(key, value)

	def fetch(self) -> dict:
		"""
		Call the api and mutate the instance variable _cached_response
		at the same time, if either none prior were made or the time 
		expired and it needs to be refreshed. 

		:returns:
			dict
		"""
		if self._cached_response:
			seconds_since_last_call = (datetime.now() - self._last_api_call).seconds
			if seconds_since_last_call < self._wait_time: 
				return self._cached_response
		try:
			response = json.loads(urlopen(self._request).read())
		except Exception:
			raise
		
		self._cached_response = response
		self._last_api_call = datetime.now()
		return response


class Client:
	"""
	Act as the interface from the retreived data 
	by an instance of the ApiHandle class.

	Return infections by country, mortalities,
	recoveries based upon method call.
	"""

	def __init__(self, api_handle: ApiHandle):
		self.api_handle = api_handle
		self.translations_file = Path(os.getcwd()).parent / 'country_eng_swe_translations.json'

	def _translate_country(self, country: str, from_language: str) -> str:
		"""
		Return the value behind key country parameter
		which is the swedish translated string of given
		country.
		:param country:
			string, country to translate
		:param from_language:
			string, from which language. Either Swedish to English or vice versa.
		:returns:
			string
		"""
		country = country.lower()
		try:
			with open(self.translations_file, 'r') as f:
				translation = json.loads(f.read())
		except Exception as e:
			raise Exception(f'Could not load translation file. {e}')
		
		if from_language == 'swedish':
			return translation['swe_to_eng'][country]
		return translation['eng_to_swe'][country]

	def get_raw_data(self):
		"""
		Returns the raw api return without any parsing.
		for debugging.
		"""
		return self.api_handle.fetch()

	def get_total_recoveries(self) -> int:
		data = self.api_handle.fetch()
		return sum([int(i['total_recovered'].replace(',', '')) for i in data['countries_stat']])

	def get_total_infections(self) -> int:
		data = self.api_handle.fetch()
		return sum([int(i['cases'].replace(',', '')) for i in data['countries_stat']])

	def get_total_deaths(self, sort_by_highest = True) -> str:
		data = self.api_handle.fetch()
		return sum([int(i['deaths'].replace(',', '')) for i in data['countries_stat']])

	def get_recoveries(self, sort_by_highest = True) -> str:
		sorter = lambda i: int(i['total_recovered'].replace(',',''))
		data = self.api_handle.fetch()
		data['countries_stat'].sort(key = sorter, reverse = sort_by_highest)
		translated_country = self._translate_country(data['countries_stat'][0]['country_name'], 'english')
		return f"{translated_country}: {data['countries_stat'][0]['total_recovered']}"

	def get_infections(self, sort_by_highest = True) -> str:
		sorter = lambda i: int(i['cases'].replace(',',''))
		data = self.api_handle.fetch()
		data['countries_stat'].sort(key = sorter, reverse = sort_by_highest)
		translated_country = self._translate_country(data['countries_stat'][0]['country_name'], 'english')
		return f"{translated_country}: {data['countries_stat'][0]['cases']}"

	def get_deaths(self, sort_by_highest = True) -> str:
		sorter = lambda i: int(i['deaths'].replace(',',''))
		data = self.api_handle.fetch()
		data['countries_stat'].sort(key = sorter, reverse = sort_by_highest)
		translated_country = self._translate_country(data['countries_stat'][0]['country_name'], 'english')
		return f"{translated_country}: {data['countries_stat'][0]['deaths']}"	

	def get_by_query(self, query: str, country_name: str) -> str:
		"""
		Get details on a country depending on query.
		:param data:
			string representing deaths, recoveries or cases. These are:
			- 'cases'
			- 'total_recovered'
			- 'deaths'
		:param country: 
			string represenging country for lookup.
		:returns:
			string
		"""

		data = self.api_handle.fetch()
		for country in data['countries_stat']:
			if country['country_name'].lower() == self._translate_country(country_name, 'swedish'):
				return country[query]
		raise KeyError(f'No such key: {country_name}')

	def get_data_timestamp(self) -> str:
		"""
		Returns the datetime string under 'statistic_taken_at' key
		in response body from the API. This indicates when the
		statistics were taken, thus how old the data is.
		:returns:
			string, datetime
		"""
		return self.api_handle.fetch()['statistic_taken_at']