from datetime import datetime
from source.weekdays import Weekdays
'''
Details:
    2019-11-24

Module details:
	Lunch menu scraping feature

Synposis:
	Provide a way for the chatbot to scrape
	the lunch menu for the restaurant in school.
	Return the menu scraped off the website.
'''

class Menu:
	'''
	Represent a menu in the form of a dictionary.
	The dictionary is formatted in weekday format,
	where 0 is monday and 4 is friday. 5 and 6
	are present, but will remain empty since the
	restaurant is closed. This will return None when 
	queried. Each value under said keys are lists
	which will contain strings that are the menu 
	items for the given day.
	'''
	def __init__(self, soup = []):
		self.soup = soup
		self._weekly_menu = {
			'måndag': [], 
			'tisdag': [], 
			'onsdag': [],
			'torsdag': [], 
			'fredag': []
		}

		self._index_lookup = {
			Weekdays.MONDAY.value: self._weekly_menu['måndag'],
			Weekdays.TUESDAY.value: self._weekly_menu['tisdag'],
			Weekdays.WEDNESDAY.value: self._weekly_menu['onsdag'],
			Weekdays.THURSDAY.value: self._weekly_menu['torsdag'],
			Weekdays.FRIDAY.value: self._weekly_menu['fredag'],
		}

		self.creation_date = datetime.today().date()
		self._serialize()

	def __getitem__(self, index):
		
		try:
			return self._index_lookup[index.value]
		except KeyError as e:
			return e
		except AttributeError:
			return f'Index must be of type Weekdays, got {type(index)}'

	def _serialize(self):
		'''
		Iterate over the HTML content found in the 
		soup object received. Look for the weekday
		markers, denoted by the keys in the 
		'''
		selected_weekday = None

		for html in self.soup:			
			if html.text.lower() in self._weekly_menu:
				selected_weekday = html.text.lower()
				continue
			
			if selected_weekday:
				self._weekly_menu[selected_weekday].append(html.text.lower())


	@property
	def creation_date(self):
		return self._creation_date

	@creation_date.setter
	def creation_date(self, value):
		self._creation_date = value
	
	@property
	def soup(self):
		return self._soup

	@soup.setter
	def soup(self, value):
		self._soup = value

	@property
	def _weekly_menu(self):
		return self._daily_menu
	
	@_weekly_menu.setter
	def _weekly_menu(self, value):
		self._daily_menu = value
