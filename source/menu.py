from datetime import datetime
from source.weekdays import Weekdays
"""
Details:
    2019-11-24

Module details:
	Lunch menu scraping feature

Synposis:
	Provide a way for the chatbot to scrape
	the lunch menu for the restaurant in school.
	Return the menu scraped off the website.
"""

class Menu:
	"""
	Represent a menu in the form of a dictionary.
	The dictionary is formatted in weekday format,
	where 0 is monday and 4 is friday. 5 and 6
	are present, but will remain empty since the
	restaurant is closed. This will return None when 
	queried. Each value under said keys are lists
	which will contain strings that are the menu 
	items for the given day.
	"""
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
			0: self._weekly_menu['måndag'],
			1: self._weekly_menu['tisdag'],
			2: self._weekly_menu['onsdag'],
			3: self._weekly_menu['torsdag'],
			4: self._weekly_menu['fredag'],
			5: None,
			6: None
		}

		self.creation_date = datetime.today().date()
		self._serialize()

	def __getitem__(self, index):
		if isinstance(index, slice):
			start, stop, step = index.indices(len(self._weekly_menu))
			return tuple(self[i] for i in range(start, stop, step))
		try:
			item = self._index_lookup[index]
		except Exception as e:
			raise Exception(e)
		return item

	def _serialize(self):
		"""
		Iterate over the HTML content found in the 
		soup object received. Look for the weekday
		markers, denoted by the keys in the 
		"""
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
	def weekly_menu(self):
		return self._daily_menu
	
	@weekly_menu.setter
	def weekly_menu(self, value):
		self._daily_menu = value
