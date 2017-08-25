from bs4 import BeautifulSoup
from happycowler import HappyCowler
from happycowler.happycowler import parse_restaurant_page
import os

data_path = '/home/pwittek/adf/'

single_restaurant_test_file = data_path + "Vegan & Vegetarian Restaurants in Singapore.htm"
with open(single_restaurant_test_file, 'r') as f:
    text = f.read()
parsed_text = BeautifulSoup(text, "html.parser")
hc = HappyCowler("", verbose=2)
hc._parse_results_page(parsed_text, page_no='', deep_crawl=False)
print(hc.names)
'''
single_restaurant_test_file = data_path + "BarCeloneta Sangria Bar - Barcelona : Vegan Restaurant Reviews and Ratings - HappyCow.htm"
with open(single_restaurant_test_file, 'r') as f:
    text = f.read()
parsed_text = BeautifulSoup(text, "html.parser")
results = parse_restaurant_page(parsed_text)
'''