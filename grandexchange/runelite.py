import requests
import json


class RuneLiteItem(object):
    def __init__(self, json):
        self.id = json['item']['id']
        self.price = json['price']
        return


class RuneLite(object):
    def __init__(self):
        self.runelite_url = 'https://api.runelite.net/runelite-1.4.2/item/price?'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }

    def items_from_future(self, future):
        return None

    def items_from_future(self, future):
        items = []

        for item_json in future.result().json():
            items.append(RuneLiteItem(item_json))

        return items

    def items_future(self, session, ids):
        parameters = ''

        is_first = True

        for id in ids:
            if is_first:
                parameters += 'id=' + str(id)
            else:
                parameters += '&id=' + str(id)

            is_first = False

        url = self.runelite_url + parameters

        return session.get(url, headers=self.headers)
