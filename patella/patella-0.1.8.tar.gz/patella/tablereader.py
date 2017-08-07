"""
This module is for reading the html tables that list world leaders off of varying webpages.
It is not very dynamic or robust, and has priority for updates.

More tables of FEs from countries around the world will be added so users can compare their data sets to different
world leaders.
"""

import pandas as pd

# A website with an html table to scrape for presidential term data
fe_url = 'http://www.enchantedlearning.com/history/us/pres/list.shtml'
fe_term_column = 2
header_row = 0
unique_text = 'Vice-President'
fe_table = pd.read_html(fe_url, match=unique_text, flavor='bs4', header=header_row,
                        index_col=fe_term_column, parse_dates=True)[0]
fe_names = []
index_list = fe_table.index.get_level_values(0).values.tolist()  # slice the data frame index as a list
year_list = []


for term in index_list:
    term_num = term.split('-')[0]  # get the first year of the term number
    year_list.append(term_num)  # add it to the year list

fe_table['Year'] = year_list
fe_table.set_index('President', drop=False, inplace=True)

#  Some formatting transformations are  required for this table. This loop sets the fe names to only alpha chars
for item in fe_table.index.get_level_values(0).values.tolist():
    fe_name = ''  # reset the name
    for char in item:  # loop through each character to check if it is alpha-nonnumeric, and append it to a string
        if char.isalpha() or char == ' ':
            fe_name = fe_name + char
    fe_names.append(fe_name)  # append the string to the presidential names list
fe_table['President'] = fe_names  # add the name list to the 'President' column of the fe dataframe
fe_table.set_index('Year', drop=True, inplace=True)  # Set the index to the year column


# A simple getter function to return the fe dataframe when needed in other modules
def get_fe():
    return fe_table
