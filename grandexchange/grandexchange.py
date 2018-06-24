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
from db import dbconnection


class GrandExchange(object):
    def __init__(self):
        self.file_path = 'data.json'
        self.all_items_url = 'https://rsbuddy.com/exchange/summary.json'
        self.setup()
        self.jagex_grand_exchange = jagex.GrandExchange()
        self.runelite = RuneLite()
        self.dbconnection = dbconnection

    def remove_keyword(self, user_id, keyword):
        return self.dbconnection.remove_keyword(user_id, keyword)

    def set_name_for_keyword(self, user_id, keyword, name):
        return self.dbconnection.set_user_group_name(user_id, keyword, name)

    def set_keyword_for_item(self, user_id, keyword, item_name):
        item_name = item_name.lower()

        if item_name not in self.name_item_mapping:
            return False, []

        # Some names have multiple items (like different colored shirts).
        # For simplicity I'm picking the first one here.
        item = self.name_item_mapping[item_name][0]

        item_group = self.dbconnection.set_keyword_for_item(user_id, keyword, item.id)

        item_names = []

        for item_id in item_group.items:
            if item_id in self.id_item_mapping:
                item_names.append(self.id_item_mapping[item_id].name)

        return True, item_names

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
        if query in self.name_item_mapping:
            return [query]

        names = self.non_greedy_search_results(query)

        if not names:
            query_results = process.extract(query, self.item_names, scorer=fuzz.partial_ratio, limit=5)

            for query_result in query_results:
                if query_result[1] > 94:
                    return [query_result[0]]

                if query_result[1] < 55:
                    break

                names.append(query_result[0])

        return names

    def item_ids_from_query(self, user_id, query):
        if ' ' not in query:
            group = self.dbconnection.item_group_for_keyword(user_id, query)
            if group is not None:
                return group.name, group.items

        item_names = self.match_names(query)

        item_ids = []
        for name in item_names:
            if name not in self.name_item_mapping:
                continue

            items = self.name_item_mapping[name]

            item_ids += [item.id for item in items]

        return None, item_ids

    def items(self, user_id, query):
        (group_name, item_ids) = self.item_ids_from_query(user_id, query)

        if len(item_ids) is 0:
            return None, []

        session = FuturesSession(executor=ThreadPoolExecutor(max_workers=8))

        jagex_futures = self.jagex_grand_exchange.futures_for_item_ids(session, item_ids)

        runelite_future = self.runelite.items_future(session, item_ids)
        runelite_items = self.runelite.items_from_future(runelite_future)
        results = []
        for index, future in enumerate(jagex_futures):
            runelite_item = runelite_items[index]
            item_id = item_ids[index]
            item = self.id_item_mapping[item_id]

            ge_item = self.jagex_grand_exchange.ge_item_from_future(future, item, runelite_item)

            results.append(ge_item)

        return group_name, results

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

        item_names = set()
        name_item_mapping = {}
        id_item_mapping = {}

        for item_id, runescape_item in item_data.items():
            name = runescape_item['name']
            name_lower = name.lower()
            shop_price = runescape_item['sp']

            item_names.add(name_lower)
            item = RunescapeItem(int(item_id), name, shop_price)

            if name_lower in name_item_mapping:
                name_item_mapping[name_lower] = name_item_mapping[name_lower] + [item]
            else:
                name_item_mapping[name_lower] = [item]

            id_item_mapping[int(item_id)] = item

        self.item_names = list(item_names)
        self.name_item_mapping = name_item_mapping
        self.id_item_mapping = id_item_mapping
