import requests
import json


class RuneLiteItem(object):
    def __init__(self, item_json):
        self.id = item_json['id']
        self.price = item_json['price']
        return


class RuneLite(object):
    def __init__(self):
        self.runelite_url = RuneLite.fetch_runelite_url()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }

    @staticmethod
    def fetch_runelite_url():
        tags_url = 'https://api.github.com/repos/runelite/runelite/tags'

        r = requests.get(tags_url)

        release_version = r.json()[0]['name'].split('-')[-1]

        return 'https://api.runelite.net/runelite-{version}/item/price?'.format(version=release_version)

    @staticmethod
    def items_from_future(future):
        items = []

        for item_json in future.result().json():
            items.append(RuneLiteItem(item_json))

        return items

    def items_future(self, session, ids):
        parameters = ''

        is_first = True

        for item_id in ids:
            if is_first:
                parameters += 'id=' + str(item_id)
            else:
                parameters += '&id=' + str(item_id)

            is_first = False

        url = self.runelite_url + parameters

        return session.get(url, headers=self.headers)


RuneLite.fetch_runelite_url()
