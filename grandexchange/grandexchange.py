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
from non_greedy_search import non_greedy_search
from .runelite import RuneLite, RuneLiteItem
from . import jagex
from .runescapeitem import RunescapeItem


class GrandExchange(object):
    def __init__(self):
        self.file_path = 'data.json'
        self.all_items_url = 'https://rsbuddy.com/exchange/summary.json'
        self.setup()
        self.jagex_grand_exchange = jagex.GrandExchange(self.item_mapping)
        self.runelite = RuneLite()

    def non_greedy_search_results(self, query):
        names_scores = []
        for name in self.item_names:
            score = non_greedy_search(name, query)
            if score >= 25:
                names_scores.append((score, name))

        names_scores = sorted(names_scores, key=lambda score_name: score_name[0], reverse=True)

        if len(names_scores) > 3:
            names_scores = names_scores[:3]

        return list(map(lambda score_name: score_name[1], names_scores))

    def match_names(self, query):
        query = query.lower()
        if query in self.item_mapping:
            return [query]

        names = self.non_greedy_search_results(query)

        if not names:
            query_results = process.extract(query, self.item_names, scorer=fuzz.partial_ratio, limit=5)

            for query_result in query_results:
                if query_result[1] > 94:
                    return [query_result[0]]

                names.append(query_result[0])

                if query_result[1] < 55:
                    break

        return names

    def single_item(self, item_name):
        result = self.multiple_items([item_name])
        return result

    def items(self, query):
        item_names = self.match_names(query)

        session = FuturesSession(executor=ThreadPoolExecutor(max_workers=8))
        items = []
        item_ids = []
        for name in item_names:
            item = self.item_mapping[name]

            if item is None:
                continue

            items.append(item)
            item_ids.append(item.id)

        jagex_futures = self.jagex_grand_exchange.futures_for_item_ids(session, item_ids)

        runelite_future = self.runelite.items_future(session, item_ids)
        runelite_items = self.runelite.items_from_future(runelite_future)
        results = []
        for index, future in enumerate(jagex_futures):
            runelite_item = runelite_items[index]
            item = items[index]

            ge_item = self.jagex_grand_exchange.ge_item_from_future(future, item, runelite_item)

            results.append(ge_item)

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
            item = RunescapeItem(id, name, shop_price)
            item_mapping[name.lower()] = item

        self.item_names = item_names
        self.item_mapping = item_mapping
