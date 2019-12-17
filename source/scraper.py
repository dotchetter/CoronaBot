from datetime import datetime
from bs4 import BeautifulSoup
from urllib import request
from source.custom_errs import ScrapingError
from source.menu import Menu
'''
Details:
    2019-11-24

Module details:
	Lunch menu scraping feature

Synposis:
	Provide a way for the chatbot to scrape
	the lunch menu for the restaurant in school.
	Return the menu scraped off the website.

	BS4 MIT License:

	Beautiful Soup is made available under the MIT license:
	Copyright (c) 2004-2019 Leonard Richardson

	Permission is hereby granted, free of charge, to any person obtaining
	a copy of this software and associated documentation files (the
	"Software"), to deal in the Software without restriction, including
	without limitation the rights to use, copy, modify, merge, publish,
	distribute, sublicense, and/or sell copies of the Software, and to
	permit persons to whom the Software is furnished to do so, subject to
	the following conditions:

	The above copyright notice and this permission notice shall be
	included in all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
	MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
	NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
	BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
	ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
	CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

	Beautiful Soup incorporates code from the html5lib library, which is
	also made available under the MIT license. Copyright (c) 2006-2013
	James Graham and other contributors
	
	Beautiful Soup depends on the soupsieve library, which is also made
	available under the MIT license. Copyright (c) 2018 Isaac Muse
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
		self._cache = None

	def _cache_menu(self, menu_obj):
		'''
		Cache the Menu object created, if there is none
		present. This reduces network traffic and increases
		response time when multiple users query the bot for
		the lunch menu simultaneously.
		'''
		if self._cache is None:
			self._cache = menu_obj

	def purge_cache(self):
		'''
		Purge the cached menu item upon call.
		'''
		self._cache = None

	@property
	def cache(self):
		return self._cache

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
		if self.cache and self.cache.creation_date == datetime.today().date():
			return self.cache

		try:
			menu = self.soup.find_all('strong')
		except Exception:
			return ScrapingError('Invalid response')
		
		for index, tag in enumerate(menu):
			if 'måndag' in tag.text.lower():
				startsat = index + 1
			elif 'kontakta' in tag.text.lower():
				endsat = index

		menu_obj = Menu(menu[startsat:endsat])
		self._cache_menu(menu_obj)
		return self.cache