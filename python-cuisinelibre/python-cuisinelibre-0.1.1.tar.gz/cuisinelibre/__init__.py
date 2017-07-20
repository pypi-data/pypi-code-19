# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import urllib.parse
import urllib.request

import re


class CuisineLibre(object):

	@staticmethod
	def search(query_dict):
		"""
		Search recipes parsing the returned html data.
		"""
		base_url = "http://www.cuisine-libre.fr/?page=recherche&"
		query_url = urllib.parse.urlencode(query_dict)

		url = base_url + query_url

		html_content = urllib.request.urlopen(url).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		search_data = []
		articles = soup.findAll("li", {"class": "clearfix"})

		for article in articles:
			data = {}
			try:
				data["name"] = article.find("a").find("strong").get_text().strip(' \t\n\r')
				data["url"] = article.find("a")['href']
				try:
					data["image"] = article.find("a").find("img")["src"][2:]
				except Exception as e1:
					pass
			except Exception as e2:
				print(e2)
				pass
			search_data.append(data)

		return search_data

	@staticmethod
	def get(uri):
		"""
		'url' from 'search' method.
		"""
		base_url = "http://www.cuisine-libre.fr/"
		url = base_url + uri

		html_content = urllib.request.urlopen(url).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		image_url = soup.find("div", {"class": "illustration"}).find("img")["src"][2:]

		ingredients_data = soup.find("div", {"class": "texte surlignable"})
		ingredients_title = ingredients_data.find("h2").get_text()

		list_ingredients_data = ingredients_data.findAll("li", {"class": "ingredient"})
		list_ingredients = [ingredient.get_text()[1:] for ingredient in list_ingredients_data]

		try:
			author = soup.find("strong", {"class": "author fn"}).get_text()
		except:
			author = "Inconnu"

		preparation_data = soup.find("div", {"id": "preparation"})
		list_instructions_data = preparation_data.findAll("p")
		list_instructions = [instr.get_text() for instr in list_instructions_data]

		data = {
			"author": author,
			"image": image_url,
			"ingredients_title": ingredients_title,
			"ingredients": list_ingredients,
			"instructions": list_instructions
		}

		return data








