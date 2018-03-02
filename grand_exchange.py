import requests
import json
import os.path
import time
import datetime
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pathlib import Path

def human_format(num):
	num = float('{:.3g}'.format(num))
	magnitude = 0
	while abs(num) >= 1000:
		magnitude += 1
		num /= 1000.0
	return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
		
def runescape_number_to_int(number):
	if isinstance(number, int):
		return number
		
	multiplier = 1
	number = number.replace('+', '')
	number = number.replace(',', '')	
	if '-' in number:
		multiplier = -1
		number = number.replace('-', '')

	if 'k' in number:
		return int(float(number.replace('k', '')) * 10**3) * multiplier
	
	if 'm' in number:
		return int(float(number.replace('m', '')) * 10**6) * multiplier
		
	if 'b' in number:
		return int(float(number.replace('b', '')) * 10**9) * multiplier
		
	return int(number) * multiplier

class GrandExchangeItem (object):
	def __init__(self, intrinsic_details, price, change):
		self.name = intrinsic_details.name
		self.alch_price = intrinsic_details.high_alch_price
		self.price = runescape_number_to_int(price)
		self.change = runescape_number_to_int(change)
				
	def log(self):
		print('{name}: {price}, change today: {change}, alch price: {alch_price}'.format(name=self.name, price=human_format(self.price), change=human_format(self.change), alch_price=human_format(self.alch_price)))

class IntrinsicItemDetails (object):
	def __init__(self, id, name, shop_price):
		self.id = id
		self.name = name
		self.high_alch_price = int(shop_price * 0.6)
		
	def result_from_json(self, json):
		json = json['item']
		price = json['current']['price']
		change = json['today']['price']
		return GrandExchangeItem(self, price, change)
		
class GrandExchange (object):
	def __init__(self):
		self.ge_base_url = 'http://services.runescape.com/m=itemdb_oldschool'
		self.ge_individual_item_path = '/api/catalogue/detail.json?item='
		self.file_path = 'data.json'
		self.all_items_url = 'https://rsbuddy.com/exchange/summary.json'
		self.setup()

	def item_url(self, id):
		url = self.ge_base_url + self.ge_individual_item_path + str(id)
		return url
	
	def match_names(self, query):
		query = query.lower()
		if query in self.item_mapping:
			print('exact match')
			return [query]
	
		query_results = process.extract(query, self.item_names, scorer=token_set_ratio, limit=5)

		names = []
		
		for query_result in query_results:
			if query_result[1] > 94:
				return [query_result[0]]
				
			names.append(query_result[0])
			
			if query_result[1] < 55:
				print('{name} score less than 40'.format(name=query_result[0]))
				break
		
		return names
			
	def single_item(self, item_name):	
		result = self.multiple_items([item_name])
		return result
	
	def items(self, query):
		coroutines = []
		
		item_names = self.match_names(query)
		
		session = FuturesSession(executor=ThreadPoolExecutor(max_workers=8))
		futures = []
		items = []
		for name in item_names:
			item = self.item_mapping[name]
			
			if item is None:
				continue
			
			items.append(item)
			
			url = self.item_url(item.id)
			
			futures.append(session.get(url))
		
		results = []	
		for index, future in enumerate(futures):
			json = future.result().json()
			item = items[index]
			results.append(item.result_from_json(json))
			
		return results
			
	def setup(self):
		file_exists = Path(self.file_path).is_file()

		if file_exists:
			file_time_struct = time.gmtime(os.path.getmtime(self.file_path))
			file_time = datetime.datetime.fromtimestamp(time.mktime(file_time_struct))
			fetch_items = not file_time > datetime.datetime.now() - datetime.timedelta(1)
		else:
			fetch_items = True
	
		if fetch_items:
			print('fetching items')
			result = requests.get(self.all_items_url)
	
			with open(self.file_path, 'w') as outfile:  
				item_data = result.json()
				json.dump(item_data, outfile)
		else:
			print('loading items from file')
			with open(self.file_path) as json_file:  
				item_data = json.load(json_file)

		item_names = []
		item_mapping = {}
		for id, object in item_data.items():
			name = object['name']
			shop_price = object['sp']
			item_names.append(name.lower())
			item = IntrinsicItemDetails(id, name, shop_price)
			item_mapping[name.lower()] = item

		self.item_names = item_names
		self.item_mapping = item_mapping	
		
	