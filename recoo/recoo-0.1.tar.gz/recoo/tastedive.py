"""
Module to interact with tastedive api
"""
from string import Template

import os
import requests
import clr

from terminaltables import AsciiTable


class TasteDiveApi(object):
    """
    All taste dive api related functions
    """

    def __init__(self):
        pass

    def print_recommendations(self, query):
        """
        Print the similar recommendations for given query
        """
        recommendations = self.get_recommendations(query)
        query_info = recommendations.get('Similar').get('Info')
        result_info = recommendations.get('Similar').get('Results')
        self.print_query_information(query_info)
        self.print_results(result_info)

    @staticmethod
    def print_query_information(query_info):
        name = query_info[0].get('Name')
        predicted_type = query_info[0].get('Type')
        print(clr.bold('Name          : '), clr.yellow(name))
        print(clr.bold('Predicted Type: '), clr.yellow(predicted_type))

    @staticmethod
    def get_recommendations(query):
        """
        Calling tastedive api with query string
        """
        taste_api_url_template = "https://tastedive.com/api/similar?k=$api_key&q=$api_query"
        taste_params = {
            'api_key': os.environ['TASTE_API_KEY'],
            'api_query': query
        }
        request_url = Template(taste_api_url_template).substitute(taste_params)
        tastedive_response = requests.get(request_url)
        return tastedive_response.json()

    @staticmethod
    def print_results(results):
        data = [["Name", "Type"]]
        data += [[result["Name"], result["Type"]] for result in results]
        table = AsciiTable(data)
        print(table.table)
