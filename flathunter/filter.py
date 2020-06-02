from functools import reduce
import re

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
