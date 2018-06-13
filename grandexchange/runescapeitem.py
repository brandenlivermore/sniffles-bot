class RunescapeItem(object):
    def __init__(self, id, name, shop_price):
        self.id = id
        self.name = name
        self.high_alch_price = int(shop_price * 0.6)
