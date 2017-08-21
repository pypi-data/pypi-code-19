from html.parser import HTMLParser
import matplotlib.pyplot as plt
import numpy as np
import matplotlib


def dict_helper(elements, hashes, cmap="tab20c"):
    # gets unique [(tag, hash)]
    tags_list = set()
    for tags, tag_hashes in zip(elements, hashes):
        for tag, tag_hash in zip(tags, tag_hashes):
            tags_list.add((tag, tag_hash))
    tags_list = list(tags_list)

    # gets colors
    color = [plt.cm.get_cmap(cmap)(val) for val in np.linspace(0, 1, len(tags_list))]
    color = [(c[0], c[1], c[2], 0.3) for c in color]
    color = [matplotlib.colors.rgb2hex(c) for c in color]

    # makes dict {tag: (color, tag_hash)}
    tags_list = list(zip(tags_list, color))
    tags_helper = dict()
    for i in tags_list:
        tags_helper[i[0][0]] = (i[1], i[0][1])

    return tags_helper


class TAParser(HTMLParser):
    def __init__(self):
        self.dict = {}
        self.last_key = None
        self.add_tit = True
        self.add_key = False
        self.add_tag = False
        self.add_ann = False
        super().__init__()


    def cases(self, tag, val, type, attrs=None):
        if tag == "h1":
            self.add_tit = val

        elif tag == "h2":
            self.add_tag = val

        elif tag == "h3":
            self.add_key = val

        elif tag == "p":
            self.add_ann = val

        elif self.add_ann:
            if type == "start":
                self.dict[self.last_key][0] += "<{0} ".format(tag)
                for i, j in attrs:
                    self.dict[self.last_key][0] += "{0}= {1}".format(i, j)
                self.dict[self.last_key][0] += ">"

            if type == "end":
                self.dict[self.last_key][0] += "</{0}>".format(tag)

    def handle_starttag(self, tag, attrs):
        self.cases(tag, True, 'start', attrs)

    def handle_endtag(self, tag):
        self.cases(tag, False, 'end')

    def handle_data(self, data):

        if self.add_key:
            self.dict[data] = ["", None]
            self.last_key = data

        elif self.add_tag:
            self.dict[self.last_key][1] = list(map(str.strip, data.split(",")))

        elif self.add_ann:
            self.dict[self.last_key][0] += data
