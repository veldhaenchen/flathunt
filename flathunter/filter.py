from functools import reduce
import re

class ExposeHelper:

    @staticmethod
    def get_price(expose):
        price_match = re.search(r'\d+([\.,]\d+)?', expose['price'])
        if price_match is None:
            return None
        return float(price_match[0].replace(",", "."))

    @staticmethod
    def get_size(expose):
        size_match = re.search(r'\d+([\.,]\d+)?', expose['size'])
        if size_match is None:
            return None
        return float(size_match[0].replace(",", "."))

class MaxPriceFilter:

    def __init__(self, max_price):
        self.max_price = max_price

    def is_interesting(self, expose):
        price = ExposeHelper.get_price(expose)
        if price is None:
            return True
        return price <= self.max_price

class MinPriceFilter:

    def __init__(self, min_price):
        self.min_price = min_price

    def is_interesting(self, expose):
        price = ExposeHelper.get_price(expose)
        if price is None:
            return True
        return price >= self.min_price

class MaxSizeFilter:

    def __init__(self, max_size):
        self.max_size = max_size

    def is_interesting(self, expose):
        size = ExposeHelper.get_size(expose)
        if size is None:
            return True
        return size <= self.max_size

class MinSizeFilter:

    def __init__(self, min_size):
        self.min_size = min_size

    def is_interesting(self, expose):
        size = ExposeHelper.get_size(expose)
        if size is None:
            return True
        return size >= self.min_size

class TitleFilter:

    def __init__(self, filtered_titles):
        self.filtered_titles = filtered_titles

    def is_interesting(self, expose):
        combined_excludes = "(" + ")|(".join(self.filtered_titles) + ")"
        found_objects = re.search(combined_excludes, expose['title'].lower())
        # send all non matching regex patterns
        if not found_objects:
            return True
        return False

class FilterBuilder:

    def __init__(self):
        self.filters = []

    def title_filter(self, filtered_titles):
        self.filters.append(TitleFilter(filtered_titles))
        return self

    def min_price_filter(self, min_price):
        self.filters.append(MinPriceFilter(min_price))
        return self

    def max_price_filter(self, max_price):
        self.filters.append(MaxPriceFilter(max_price))
        return self

    def min_size_filter(self, min_size):
        self.filters.append(MinSizeFilter(min_size))
        return self

    def max_size_filter(self, max_size):
        self.filters.append(MaxSizeFilter(max_size))
        return self

    def build(self):
        return Filter(self.filters)

class Filter:

    def __init__(self, filters):
        self.filters = filters

    def is_interesting_expose(self, expose):
        return reduce((lambda x, y: x and y), map((lambda x: x.is_interesting(expose)), self.filters), True)

    def filter(self, exposes):
        return filter(lambda x: self.is_interesting_expose(x), exposes)

    @staticmethod
    def builder():
        return FilterBuilder()
