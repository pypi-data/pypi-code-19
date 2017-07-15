import re, os, glob
from urllib.parse import *
from io import BytesIO
from queue import Queue
from itertools import product
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import namedtuple, OrderedDict

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm



def urlencode_sorted(params_dict):
	return urlencode({k: params_dict[k] for k in sorted(params_dict)})



class Scraper:
	
	def __init__(self, root, auth_path=None, save_root='.', headers=None, max_worker=10):
		'''Scraper(root='http://www.abcd.com', auth_path=/Auth/Login/, save_root='.')
			save_root: Download Folder, auth_path: Login Page Path
		'''
		self.root = root
		self.headers = headers
		self.save_root = save_root
		self.auth_url = root + auth_path if auth_path else None
		self.max_worker = max_worker
		self.session = requests

	def _product_params(self, **params_set):
		'''prod_params(prodtype=['E', 'O', 'Q'], MktStats=['AS', 'AE', 'AD'], kdcode=['86147', '1231'], page=range(5))
		'''
		return [dict(zip(params_set.keys(), args)) for args in product(*params_set.values())]


	def _login(self, abs_auth_url=None,  **login_data):
		'''set login Form Fields values, autocompletes other hidden fields
			_login(**{'user_id': 'ABCD', 'user_pwd': '1234'}) or _login(user_id='ABCD', user_pwd='1234')
		'''
		r = requests.get(abs_auth_url or self.auth_url)
		soup = BeautifulSoup(r.content, 'html.parser')
		for form in soup('form'):
			if all(form.find('input', {'name': name}) for name in login_data):
				for inp in form('input', {'name':re.compile(r'.+')}):
					name = inp['name']
					if name not in login_data:
						login_data[name] = inp['value']
				session = requests.Session()
				session.post(r.url, login_data)
				self.session = session


	def _get_page_soup(self, path, params=None, data=None):
		if data:
			r = self.session.post(self.root+path, data=data, headers=self.headers)
		r = self.session.get(self.root+path, params=params, headers=self.headers)
		return BeautifulSoup(r.content, 'html.parser')


	def save_url(self, path, params=None, data=None, overwrite=False, sep='=='):
		''' sep: concaternator path and querysting for save filename
		'''
		url = self.root + path
		tokken = [self.save_root+path]

		tokken.append(urlencode_sorted(data or params or ''))
		_file = sep.join(tokken)
		
		if os.path.exists(_file) and not overwrite:
			return 
		
		os.makedirs(os.path.dirname(_file), exist_ok=True)

		r = self.session.post(url, data, headers=self.headers) if data else self.session.get(url, params=params, headers=self.headers)

		if r.status_code != 200:
			return 
		
		with open(_file, 'wb') as fp:
			fp.write(r.content)


	def save_urls_with_params(self, src_path, overwrite=False, sep='==', **params_set):
		'''DownLoad url with all avaliable params combination cases
		   save_urls_with_params('/A/B/C', **{'prodtype': ['A','B', 'C'], 'Page':range(1, 11)})
		   -> 3 x 10 = 30,(prodtype_len=3, Page_len=10) this code will scraping 30 cases of request
		'''
		args_list =[]
		for param in self._product_params(**params_set):
			args = src_path, param, None, overwrite, sep
			args_list.append(args)

		ret = []
		with ThreadPoolExecutor(min(len(args), self.max_worker)) as executor:
			todo_list = []
			for args in args_list:
				future = executor.submit(self.save_url, *args)
				todo_list.append(future)

			done_iter = tqdm(as_completed(todo_list), total=len(todo_list))
			for future in done_iter:
				soup = future.result()
			return ret



	def extract_href(self, urlpattern, src_path, src_params=None, src_data=None,  **params_set):
		'''if not param_set, extract href for only one page, but also set params_set like this,
			extract_href(r'^/A/B/.+$', '/A/List/', **{'prodtype': ['A','B', 'C'], 'Page':range(1, 11)})
			will extract href from src_path with all combination ['A', 'B', 'C'], range(1,11) (30 cases) 
		'''
		if not params_set:
			soup = self._get_page_soup(src_path, src_params, src_data)
			return [tag['href'] for tag in soup(href=re.compile(urlpattern))]

		args_list =[]
		for param in self._product_params(**params_set):
			args = src_path, param, None,
			args_list.append(args)

		ret = []
		with ThreadPoolExecutor(min(len(args), self.max_worker)) as executor:
			todo_list = []
			for args in args_list:
				future = executor.submit(self._get_page_soup, *args)
				todo_list.append(future)

			done_iter = tqdm(as_completed(todo_list), total=len(todo_list))
			for future in done_iter:
				soup = future.result()
				ret += [tag['href'] for tag in soup(href=urlpattern)]
			return ret
				
