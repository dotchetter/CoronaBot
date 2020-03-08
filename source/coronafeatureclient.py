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

	:uri:
		URI for the REST api

	:_last_api_call:
		datetime stamp for when data was most recently fetched
		from the api, used to return cache within the defined
		span upon construction, minmum 0 hours.

	:_wait_time:
		seconds calculated by the defined standby_hours parameter

	:_cached_response:
		last response received by the API

	:
	"""

	def __init__(self, uri: str, standby_hours = 2):
		self.uri: str = uri
		self.last_api_call: datetime = None
		self._wait_time = (60 * 60) * standby_hours
		self._cached_response = None
		self._cached_response: dict = None
		self._headers = {}

		try:
			self.fetch()
		except Exception as e:
			return f'ApiHandle error: The request failed:\n{e}'

	@property
	def uri(self) -> str:
		return self._uri
	
	@uri.setter
	def uri(self, uri: str) -> None:
		if uri.startswith('https'):
			self._uri = uri
		else:
			raise AttributeError('Got "http", expected "https"')
	
	@property
	def last_api_call(self) -> str:
		"""
		Return property in string format for easy readability
		for users.
		"""
		return self._last_api_call.strftime("%Y-%m-%d %H:%M")

	@last_api_call.setter
	def last_api_call(self, val: datetime) -> None:
		self._last_api_call = val

	def add_header(self, key: str, value: str) -> None:
		"""
		Allows this object to add HTML headers for the 
		request. The method is meant to be used prior to
		a call for an API which requires headers to work.

		:param key:
			str
			the key in the header, example: 'User-Agent'
		:param vaue:
			str
			The value behind said key.
		:returns:
			None
		"""
		self._headers[key] = value

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
			response = requests.get(self.uri, headers = self._headers).json()
		except Exception:
			raise
		
		self._cached_response = response
		self.last_api_call = datetime.now()
		return response



class Client:
	"""
	Act as the interface from the retreived data 
	by an instance of the ApiHandle class.

	Return infections by country, mortalities,
	recoveries based upon method call.
	"""

	def __init__(self, api_handle: ApiHandle, translation_file_path: str):
		self.api_handle = api_handle
		self.translation_file_path = translation_file_path

	def _translate(self, country: str, from_language: str) -> str:
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
			with open(self.translation_file_path, 'r') as f:
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
		return sum([int(i['recovered']) for i in data])

	def get_total_infections(self) -> int:
		data = self.api_handle.fetch()
		return sum([int(i['cases']) for i in data])

	def get_total_deaths(self, sort_by_highest = True) -> str:
		data = self.api_handle.fetch()
		return sum([int(i['deaths']) for i in data])

	def get_recoveries(self, sort_by_highest = True) -> str:
		sorter = lambda i: int(i['recovered'])
		data = self.api_handle.fetch()
		data.sort(key = sorter, reverse = sort_by_highest)
		translated_country = self._translate(data[0]['country_name'], 'english')
		return f"{translated_country}: {data[0]['recovered']}"

	def get_infections(self, sort_by_highest = True) -> str:
		sorter = lambda i: int(i['cases'])
		data = self.api_handle.fetch()
		data.sort(key = sorter, reverse = sort_by_highest)
		translated_country = self._translate(data[0]['country_name'], 'english')
		return f"{translated_country}: {data[0]['cases']}"

	def get_deaths(self, sort_by_highest = True) -> str:
		sorter = lambda i: int(i['deaths'])
		data = self.api_handle.fetch()
		data.sort(key = sorter, reverse = sort_by_highest)
		translated_country = self._translate(data[0]['country_name'], 'english')
		return f"{translated_country}: {data[0]['deaths']}"	

	def get_by_query(self, query: str, country_name: str) -> str:
		"""
		Get details on a country depending on query.
		:param data:
			string representing deaths, recoveries or cases. These are:
			- 'cases'
			- 'recovered'
			- 'deaths'
		:param country: 
			string represenging country for lookup.
		:returns:
			string
		"""

		data = self.api_handle.fetch()
		for country in data:
			if country['country'].lower() == self._translate(country_name, 'swedish'):
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
		return self.api_handle.last_api_call