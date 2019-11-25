from datetime import datetime
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
		self.daily_menu = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}
		self.todays_menu = self.serialize()[datetime.now().weekday()]
		
	def __repr__(self):
		if not len(self):
			return None
		self.todays_menu = [f'**{i}**\n' for i in self.todays_menu]
		return str().join(self.todays_menu)

	def __len__(self):
		return len(self.todays_menu)

	def serialize(self):
		'''
		Return dictionary representation of the items
		in self.soup. Divide the menu in to dict keys
		corresponding to weekday indexing, and add any
		lines of text to corresponsing list in the dict.
		'''
		swe_weekdays = ['måndag','tisdag',
						'onsdag','torsdag', 
						'fredag']
		key_count = 0
		for item in self.soup:
			if item.text.lower() in swe_weekdays:
				key_count += 1
				continue
			self.daily_menu[key_count].append(item.text)
		return self.daily_menu
	
	@property
	def soup(self):
		return self._soup

	@soup.setter
	def soup(self, value):
		self._soup = value

	@property
	def daily_menu(self):
		return self._daily_menu
	
	@daily_menu.setter
	def daily_menu(self, value):
		self._daily_menu = value