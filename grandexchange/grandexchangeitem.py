from numberformatter import runescape_number_to_int


class GrandExchangeItem(object):
    def __init__(self, intrinsic_details, price, change, icon):
        self.name = intrinsic_details.name
        self.alch_price = intrinsic_details.high_alch_price
        self.price = price
        self.change = runescape_number_to_int(change)
        self.icon = icon
