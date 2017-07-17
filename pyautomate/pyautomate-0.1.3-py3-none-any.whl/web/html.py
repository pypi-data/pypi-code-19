# coding: utf-8
import importlib
import pandas as pd
from bs4 import BeautifulSoup


class Html(BeautifulSoup):
    def __init__(self, html):
        parser = 'lxml' if importlib.util.find_spec('lxml') else 'html.parser'
        encoding = None if isinstance(html, str) else 'utf-8'
        super().__init__(html, parser, from_encoding=encoding)

    def extract_tables(self, selector):
        table_elements = self.select(selector)
        table_frames = pd.read_html(str(table_elements))
        return table_frames[0] if len(table_frames) == 1 else table_frames
