from functools import reduce
import re

from flathunter.idmaintainer import AlreadySeenFilter

class ExposeHelper:

    @staticmethod
    def get_price(expose):
        price_match = re.search(r'\d+([\.,]\d+)?', expose['price'])
        if price_match is None:
            return None
        return float(price_match[0].replace(".", "").replace(",", "."))

    @staticmethod
    def get_size(expose):
        size_match = re.search(r'\d+([\.,]\d+)?', expose['size'])
        if size_match is None:
            return None
        return float(size_match[0].replace(",", "."))

    @staticmethod
    def get_rooms(expose):
        rooms_match = re.search(r'\d+([\.,]\d+)?', expose['rooms'])
        if rooms_match is None:
            return None
        return float(rooms_match[0].replace(",", "."))

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

class MaxRoomsFilter:

    def __init__(self, max_rooms):
        self.max_rooms = max_rooms

    def is_interesting(self, expose):
        rooms = ExposeHelper.get_rooms(expose)
        if rooms is None:
            return True
        return rooms <= self.max_rooms

class MinRoomsFilter:

    def __init__(self, min_rooms):
        self.min_rooms = min_rooms

    def is_interesting(self, expose):
        rooms = ExposeHelper.get_rooms(expose)
        if rooms is None:
            return True
        return rooms >= self.min_rooms

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

class PredicateFilter:

    def __init__(self, predicate):
        self.predicate = predicate

    def is_interesting(self, expose):
        return self.predicate(expose)

class FilterBuilder:

    def __init__(self):
        self.filters = []

    def read_config(self, config):
        if "excluded_titles" in config:
            self.filters.append(TitleFilter(config["excluded_titles"]))
        if "filters" in config and config["filters"] is not None:
            filters_config = config["filters"]
            if "excluded_titles" in filters_config:
                self.filters.append(TitleFilter(filters_config["excluded_titles"]))
            if "min_price" in filters_config:
                self.filters.append(MinPriceFilter(filters_config["min_price"]))
            if "max_price" in filters_config:
                self.filters.append(MaxPriceFilter(filters_config["max_price"]))
            if "min_size" in filters_config:
                self.filters.append(MinSizeFilter(filters_config["min_size"]))
            if "max_size" in filters_config:
                self.filters.append(MaxSizeFilter(filters_config["max_size"]))
            if "min_rooms" in filters_config:
                self.filters.append(MinRoomsFilter(filters_config["min_rooms"]))
            if "max_rooms" in filters_config:
                self.filters.append(MaxRoomsFilter(filters_config["max_rooms"]))
        return self

    def max_size_filter(self, size):
        self.filters.append(MaxSizeFilter(size))
        return self

    def predicate_filter(self, predicate):
        self.filters.append(PredicateFilter(predicate))
        return self

    def filter_already_seen(self, id_watch):
        self.filters.append(AlreadySeenFilter(id_watch))
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
