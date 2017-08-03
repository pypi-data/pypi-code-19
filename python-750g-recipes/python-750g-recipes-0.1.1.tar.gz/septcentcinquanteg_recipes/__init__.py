# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import urllib.parse
import urllib.request

import re, ipdb


class Recipes(object):

	@staticmethod
	def search(query_dict):
		"""
		Search recipes parsing the returned html data.
		"""
		url = "http://www.750g.com/recettes_%s.htm" % (query_dict["recherche"].replace(" ", "_"))

		html_content = urllib.request.urlopen(url).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		search_data = []
		articles = soup.findAll("section", {'class': re.compile('recipe-\d+')})

		for article in articles:
			data = {}
			try:
				data["name"] = article.find("h2", {"class": "c-row__title c-recipe-row__title"}).get_text().strip(' \t\n\r')
				data["url"] = article.find("a", {"class": "u-link-wrapper"})['href']
				data["desc"] = article.find("p", {"class": "c-row__desc"}).get_text().strip(' \t\n\r')
				try:
					data["image"] = article.find("div", {"class": "c-row__media c-recipe-row__media"}).find("img")["data-src"]
				except Exception as e1:
					data["image"] = ""
					pass
			except Exception as e2:
				ipdb.set_trace()
				print(e2)
				pass
			search_data.append(data)

		return search_data

	@staticmethod
	def get(uri):
		"""
		'url' from 'search' method.
		"""
		base_url = "http://www.750g.com"
		url = base_url + uri

		html_content = urllib.request.urlopen(url).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		try:
			image_url = soup.find("picture").find("img")["src"]
		except:
			image_url = ""

		ingredients_data = soup.find("div", {"class": "u-margin-vert u-border-top u-border-bottom"})
		ingredients_title = ingredients_data.find("h2").get_text()

		list_ingredients_data = ingredients_data.findAll("li", {"class": "ingredient"})
		list_ingredients = [ingredient.get_text().replace('\n', '').strip() for ingredient in list_ingredients_data]

		try:
			author = soup.find("strong", {"class": "author fn"}).get_text()
		except:
			author = "Inconnu"

		preparation_data = soup.find("div", {"class": "c-recipe-steps"})
		list_instructions_data = preparation_data.findAll("div", "c-recipe-steps__item-content")

		list_instructions = []
		for instr in list_instructions_data:
			for br in instr.find_all("br"):
			    br.replace_with("\n")
			list_instructions.append(instr.get_text())

		data = {
			"author": author,
			"image": image_url,
			"ingredients_title": ingredients_title,
			"ingredients": list_ingredients,
			"instructions": list_instructions
		}

		return data








