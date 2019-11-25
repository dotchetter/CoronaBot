from datetime import datetime
from bs4 import BeautifulSoup
from urllib import request
from custom_errs import ScrapingError
from menu import Menu
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

class Scraper:
	'''
	Scrape the website for the lunch restaurant.
	Return dict with comprehended text from a 
	parsed website. Look for defined tag using
	bs4, and ignore tags that are not of interest
	when looking for the lunch menu.
	'''

	def __init__(self, url = None):
		self.url = url

	@property
	def url(self):
		return self._url

	@url.setter
	def url(self, value):
		self._url = value

	@property
	def response(self):
		try:
			r = request.urlopen(self.url)
		except Exception as e:
			return None
		return r.read() if r.status == 200 else None	

	@property
	def soup(self):
		if self.response is not None:
			return BeautifulSoup(self.response, 'html.parser')
		else:
			return None

	def get(self):
		'''
		Scrape the website for menu text. Returns Menu
		instance.
		'''
		try:
			menu = self.soup.find_all('strong')
		except Exception:
			return ScrapingError('Invalid response')
		
		for index, tag in enumerate(menu):
			if 'måndag' in tag.text.lower():
				startsat = index + 1
			elif 'kontakta' in tag.text.lower():
				endsat = index
		return Menu(menu[startsat:endsat])
