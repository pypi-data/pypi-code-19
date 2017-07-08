from bs4 import BeautifulSoup
import re, html, math, json, lxml

class html_merge:
    def __init__(self, str_html):
        self.soup = BeautifulSoup(str_html, 'lxml')
        self.good_soup = html.unescape(self.soup)
        self.multiplier_constant = 1.2364
        self.banished_words = ['st', 'rd', 'th']

    def merge_elements(self):
        soup = self.good_soup.find('body')
        span_dict = {}

        for span in soup.children:
            if span.name == 'div':
                span_dict[span.string] = span
            elif span.name == 'span':
                height = re.search('(?<=height:)[^px]*', span['style'])
                width = re.search('(?<=width:)[^px]*', span['style'])
                current_top_px = int(re.search('(?<=top:)[^px]*', span['style']).group(0))

                if height is None:
                    height_threshold = 4
                else:
                    height_threshold = int(height.group(0))

                if height_threshold < 5:
                    if not height_threshold:
                        new_width = math.floor(int(width.group(0)) * self.multiplier_constant)
                        span['style'] = span['style'].replace(str(width.group(0)), str(new_width))

                    left_px = int(re.search('(?<=left:)[^px]*', span['style']).group(0))
                    if current_top_px not in span_dict.keys():
                        letter = span.string
                        span.string = json.dumps({left_px: letter})
                        span_dict[current_top_px] = span
                    else:
                        if span_dict[current_top_px].string:
                            letter_dict = json.loads(span_dict[current_top_px].string)
                            letter_dict[left_px] = span.string
                            new_string = json.dumps(letter_dict)
                            span_dict[current_top_px].string = new_string
                else:
                    pass
            else:
                pass
        return span_dict

    def combine_elements_to_html(self, span_dict):
        finished_html = "<html>"
        for span in span_dict.values():
            if span.name == 'div':
                try:
                    finished_html += str(new_div)
                except NameError:
                    pass
                new_div = self.good_soup.new_tag('div')
                new_div.attrs['class'] = 'page'
            else:
                word_dict = json.loads(span.string)
                word = ''
                spans = []
                sorted_keys = sorted(word_dict.keys(), key=int)

                height = re.search('(?<=height:)[^px]*', span['style'])
                current_span_left = re.search('(?<=left:)[^px]*', span['style']).group(0)
                first_left = sorted_keys[0]
                if int(current_span_left) > int(first_left):
                    span['style'] = span['style'].replace(current_span_left, first_left)

                len_keys = len(sorted_keys)
                for i in range(len_keys):
                    current_key = sorted_keys[i]
                    try:
                        next_key = sorted_keys[i + 1]
                        current_letter = word_dict[current_key]
                        next_letter = word_dict[next_key]

                        px_diff = int(next_key) - int(current_key)
                        if px_diff > 20:
                            if word:
                                prev_span = self.good_soup.new_tag('span')
                                prev_span.string = word
                                spans.append(prev_span)
                                word = ''

                            new_span = self.good_soup.new_tag('span')
                            new_span.attrs['style'] = 'width:{}px;display:inline-block;'.format(px_diff * self.multiplier_constant)
                            spans.append(new_span)
                        else:
                            current_letter = word_dict[current_key]
                            if current_letter is not None:
                                word += current_letter
                    except IndexError:
                        current_letter = word_dict[current_key]
                        if current_letter is not None:
                            word += current_letter

                new_span = self.good_soup.new_tag('span')
                new_span.string = word
                if word != '' and word != "":
                    spans.append(new_span)
                    span.contents = spans
                else:
                    span.contents = []

                if height is None:
                    extra_attrs = 'white-space: pre; width: 100%;'
                    span['style'] += extra_attrs
                    span.attrs['class'] = 'line'
                if not(len(word) == 2 and word in self.banished_words):
                    new_div.contents.append(span)

        finished_html += "</html>"
        return finished_html

    def run(self):
        merged = self.merge_elements()
        combined = self.combine_elements_to_html(merged)
        return combined

def main():
    print('hello world')

if __name__ == '__main__':
    main()
