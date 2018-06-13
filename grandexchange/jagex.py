from .grandexchangeitem import GrandExchangeItem


class GrandExchange(object):
    def __init__(self, item_mapping):
        self.ge_base_url = 'http://services.runescape.com/m=itemdb_oldschool'
        self.ge_individual_item_path = '/api/catalogue/detail.json?item='

        self.item_mapping = item_mapping

    def item_url(self, item_id):
        url = self.ge_base_url + self.ge_individual_item_path + str(item_id)
        return url

    def futures_for_item_ids(self, session, item_ids):
        futures = []
        for id in item_ids:
            url = self.item_url(id)
            futures.append(session.get(url))

        return futures

    def ge_item_from_future(self, future, jagex_item, runelite_item):
        json = future.result().json()
        return self.ge_item(jagex_item, json, runelite_item)

    def ge_item(self, jagex_item, jagex_detail_json, runelite_item):
        json = jagex_detail_json['item']
        price = runelite_item.price
        change = json['today']['price']
        return GrandExchangeItem(jagex_item, price, change)
