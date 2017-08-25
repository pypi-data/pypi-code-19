import re
from bs4 import BeautifulSoup


class Soup:
    def __init__(self, *args, **kwargs):
        self.soup = BeautifulSoup(*args, **kwargs)

    def get_title(self):

        if self.soup.title is None:
            return None
        text = str(self.soup.title.get_text())
        return re.sub('\s+', ' ', text)

    def get_text(self):
        texts = self.soup.findAll(text=True)

        def visible(element):
            if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                return False
            elif re.match('<!--.*-->', str(element)):
                return False
            return True

        visible_texts = filter(visible, texts)
        return ' '.join(visible_texts)

    def get_links(self):
        return list(set([link['href'] for link in self.soup.find_all('a', href=True) if
                link['href'] != '/' and not link['href'].startswith('java')]))

    def get_links2(self):
        return list(set([style['href'] for style in self.soup.find_all('link', href=True)]))

    def get_images(self):
        srcs = [img['src'] for img in self.soup.find_all('img', src=True) if img.get('src') is not None]
        data_srcs = [img.get('data.src') for img in self.soup.find_all('img', src=False) if
                     img.get('data-src') is not None]
        return list(set(srcs + data_srcs))

    def get_scripts(self):
        return list(set([script['src'] for script in self.soup.find_all('script', src=True)]))

    def get_metas(self):
        return list(set([meta.get('content') for meta in self.soup.find_all('meta', content=True)]))
