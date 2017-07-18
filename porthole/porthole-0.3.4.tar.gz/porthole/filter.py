"""
We want to be able to split up query results according to an arbitrary attribute in the result data.

Two approaches -
(1) Execute query multiple times, each time w a different value for a given parameter.
(2) Execute query once and split results.

(2) is probably more performant, given db and network costs.
"""

from random import randint, choice


class ResultFilter(object):
    def __init__(self, headers, data, filter_by):
        self.headers = headers
        self.data = data
        self.filter_by = filter_by
        self.filtered_data = {}
        try:
            self.filter_idx = headers.index(filter_by)
        except:
            raise ValueError("Provided headers must contain filter_by value.")

    def filter(self):
        self.keys = []
        for row in data:
            key = row[self.filter_idx]
            if key not in self.keys:
                self.keys.append(key)
                self.filtered_data[key] = []
            self.filtered_data[key].append(row)

    def __iter__(self):
        self.pos = 0
        self.end = len(self.keys) - 1
        return self

    def __next__(self):
        if self.pos <= self.end:
            self.pos += 1
            key = self.keys[self.pos - 1]
            return key, self.filtered_data[key]
        else:
            raise StopIteration


fields = ['Name', 'Number']
names = ['Billy', 'Erika', 'Bodoni']
data = [[choice(names), randint(0,100)] for _ in range(0,100)]

test_filter = ResultFilter(headers=fields, data=data, filter_by='Name')
test_filter.filter()
# for key in test_filter.keys:
#     print(test_filter.filtered_data[key])
for key, data in test_filter:
    print(key, data)
