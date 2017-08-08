# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
This module has two important functions:

htmlparser.find_download_links(): this function is used to scrape webpages for download links and html tables,
                                  allowing users to find and download items from a page.

htmlparser.compare(): this function is used to compare some data frame with a date column in it to the years in office
                      of the relevant president or party in office at the time.
"""

'''\/ Local Imports \/'''
from .tablereader import get_fe

''' \/ Third-Party Imports \/ '''
from bokeh import plotting
import bokeh.palettes as palettes
from bokeh.embed import components
from flask import render_template
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
import os
import urllib.request
import logging
import datetime
from dateparser import parse

logging.basicConfig(filename='webservice.log', level=logging.DEBUG )  # set up the logger at level debug


def prlog(msg, log=True, prnt=False, level='ERROR'):
    """
    :type log: bool
    :param msg: msg to print/log
    :param log: if the function should log the msg or not
    :param prnt: if the function should print the msg or not
    :param level: what level the logger records the message at
    :return: None
    """

    if prnt:
        print(msg)
    elif log:
        print("logging." + level)
        logging.error(msg)



def download_approved(ext, filep):
    """
    A function that returns true if the file extension is correct AND the file is readable
    :param ext: the expected file extension of the file
    :param filep: the filepath of the file
    :return: True if approved, False if not
    """
    approved_exts = ['.csv', '.tsv']
    delim = ''  # namespace scope expansion
    problem = 'none'  # by default, no problems
    for item in approved_exts:
        if ext == item:
            if item is '.csv':
                delim = ','
            elif item is '.tsv':
                delim = '\t'
            else:
                problem = 'some'  # if problem, some problem
    try:
        filep.encode('utf-8').strip()
        pd.read_table(filep, delim, header=0, engine='python')
    except Exception as exc:  # if problem, some problem
        logging.error(exc)
        problem = 'some'
    if problem == 'none':
        return True
    elif problem == 'some':
        return False



def previous_element(_list, index):
    """
    A function which defines the previous elemenet in a list - makes the code more readable
    """
    return _list[index-1]



def find_download_links(url, filetype, output_name, in_number=0, download=False, clobber=True):

    """
    # A function which looks around webpages for html tables and .csv/.tsv download links and downloads them.
    :param url: url to be scraped
    :param filetype: filetype to look for in the scraped url
    :param output_name: name of the file to be downloaded
    :param in_number: the number by order of the link in the url
    :param download: if the function should download a file or just return
    :param clobber: if files with the same name should be clobbered
    :return: a dictionary that returns an error as 'error', the outputname as 'filename'
             and the list of links in the url as 'href_list'
    """
    error = 'None'
    p_url = urlparse(url)
    domain = '{urm.scheme}://{urm.netloc}'.format(urm=p_url)  # using outdated urllib1 - this line obtains domain
    dl_name = output_name  # set to the output name by default if no transformations are needed
    link_list = []
    no_tags = ''
    ext_length = len(filetype)
    extension = url[-ext_length:]
    output_path = os.getcwd() + '/data/' + dl_name
    log_message = 'file downloaded succesfully as ' + dl_name + extension + 'from ' + no_tags
    if filetype == output_name[-ext_length:]:   # Format the file name so user input is flexible
        dl_name = output_name[:len(output_name)-ext_length]   # Can include file extension or none
    # First and foremost, check if the user is entering a valid data format
    if extension == filetype:
        link_list.append(url)   # Before anything, check if the url entered IS a dl link
        if download and clobber:  # check if directory exists, check if file is parseable, check allowed file extensions
            urllib.request.urlretrieve(url, output_path)
            if not download_approved(extension, output_path):
                os.remove(output_path)
            else:
                prlog('file downloaded successfully as ' + dl_name)
    else:
        r = urllib.request.urlopen(url)
        soup = BeautifulSoup(r, 'html.parser')
        for link in soup.find_all('a', string=True):   # look through the link tags as strings
            no_tags = link.get('href')
            logging.info(str(no_tags))
            if filetype == str(no_tags)[-ext_length:]:   # Check the three letter file extension
                if 'http://' not in no_tags and 'https://' not in no_tags:   # If no first part of the url, add it
                    no_tags = domain + '/' + no_tags
                link_list.append(no_tags)
        if download and clobber:
            if no_tags is not None:   # Null check
                if len(link_list) == 1:
                    prlog("One link found: " + no_tags)
                    urllib.request.urlretrieve(no_tags, output_path)
                    if not download_approved(extension, output_path):
                        os.remove(output_path)
                    else:
                        prlog(log_message)
                elif len(link_list) > 1:
                    for idx, item in enumerate(link_list):
                        prlog(str(idx) + '. ' + item)
                    if int(in_number) <= len(link_list):
                        no_tags = link_list[int(in_number)]
                        urllib.request.urlretrieve(no_tags, output_path)
                        if not download_approved(extension, output_path):
                            os.remove(output_path)
                        else:
                            prlog(log_message)
                    else:
                        error = 'No link found with that number (' + str(in_number) + ')'
                else:
                    error = 'No links found!'
            elif filetype not in str(no_tags):
                error = 'No file found for that extension (' + filetype + ')'
    prlog(error)
    return {'error': error, 'download_name': dl_name, 'href_list': link_list}



def file_to_htmltable(filepath, delim=','):
    """
    simple function to take a file from a file path and generate an html table
    :return: html table script as 'htmltable' variable
    """
    dataframe = pd.read_table(filepath, delim, header=0, engine='python')
    htmltable = dataframe.to_html(bold_rows=True, escape=True)
    return htmltable



def compare(df1, col, title, x_lb, y_lb,
            fedf=get_fe(),
            year_col='Year',
            html='plotlocal.html',
            render=True,
            urlth='patella'
            ):
    """
    A function that takes a dataframe for input and compares it to the change by year as a political party held power
    :param df1: the first data frame to be compared.
    :param fedf: the second dataframe to be compared, always fe_list.
    :param col: the data column of the first data frame which holds the dates needed to be compared.
    :param title: the title of the plot to be exported.
    :param x_lb: the title of the x axis for the exported plot.
    :param y_lb: the title of the y axis for the exported plot.
    :param year_col: the titel of column of the data frame input to set as the index
    :param html: the html page to be rendered
    :param render: if the function should return js components for a bokeh plot or just the input/resulting dataframes
    :param urlth: the path the url takes to render
    :return: a render_template object which sends a bokeh js/html/css plot to the page as well as a special div.
    """

    data_col = int(col)-1  # subtract 1 from it so the column counting starts from one in the input
    df1.set_index(year_col, drop=True, inplace=True) # if year_col and type(year_col) is "string" else prlog('year col not string')
    ind_list = [parse(str(int(x))).year for x in df1.index.get_level_values(0).values.tolist()]
    office_yr_list = []
    party_office_list = []
    yrs_in_office = 1
    party_yrs_in_office = 1
    term_st_list = fedf.index.get_level_values(0)
    totalfe_list = []
    totalparty_list = []

    # populate a list with tuples of the year and the index where the year changes by looping through the index of the
    # data frame, which is the year column. This spits out a tuple that looks like (years, number of data points)
    # afterwards , the lists interval and years_list are used to store the parts of the tuple individually
    year_and_interval_list = [(i, previous_element(ind_list, i)) for i, year in
                              enumerate(ind_list) if i >= 1 and previous_element(ind_list, i) != ind_list[i]]
    interval = [tpl[0] for tpl in year_and_interval_list]
    years_list = [tpl[1] for tpl in year_and_interval_list]
    total_chg = [(df1.iloc[0, data_col]-df1.iloc[interval[i], data_col]) if i == 0
                 else (df1.iloc[previous_element(interval, i), data_col] - df1.iloc[interval[i], data_col]) if interval[i] < len(ind_list)
                 else (df1.iloc[previous_element(interval, i), data_col] - df1.iloc[(len(ind_list) - previous_element(interval, i)), data_col])
                 for i, item in enumerate(years_list)]

    # A list of variation from year to year, created by dividing the list at index by the previous element,
    # then multiplying by 100 to get a percentage value.
    cov_list = [total_chg[i]/df1.iloc[interval[i], data_col]*100 if previous_element(total_chg, i) != 0
                else total_chg[i] for i, n in enumerate(years_list)]

    # Create lists of all the parties and years over all the us years by finding the distance from from the first
    # presidential term served to the last and appending incremented years in that range to the totalfe totalparty lists
    for idx, item in enumerate(term_st_list):
        if idx != len(term_st_list)-1:
            dist = int(term_st_list[idx+1]) - int(item)
        else:
            dist = datetime.datetime.now().year - int(item) + 1
        for n in range(dist):
            totalfe_list.append(fedf.iloc[idx, 0])
            totalparty_list.append(fedf.iloc[idx, 1])
    # A list of all years there have been presidents
    us_years = [yr+int(term_st_list[0]) for yr in range(int(term_st_list[-1]) - int(term_st_list[0]))]
    # A list of all the parties over every year of the data set
    party_list = [totalparty_list[i] for i, item in enumerate(us_years) for years in years_list if years == item]
    # A list of all the fes over every year of the data set
    fe_list = [totalfe_list[i] for i, item in enumerate(us_years) for years in years_list if years == item]
    # Make the 'years in office' and 'party in office' lists by finding the number of consecutive
    # a party/fe was in office
    # list comprehension possible?
    for idx, item in enumerate(fe_list):
        if idx >= 1 and fe_list[idx - 1] == fe_list[idx]:   # After at least one loop (to avoid oob error) and if the index doesnt change
            yrs_in_office += 1  # increment 1
        else:
            yrs_in_office = 1  # reset to year 1
        office_yr_list.append(yrs_in_office)   # append the year number
    for idx, item in enumerate(party_list):
        if idx >= 1 and party_list[idx - 1] == party_list[idx]:  # After at least one loop (to avoid oob error) and if the index doesnt change
            party_yrs_in_office += 1  # increment 1
        else:
            party_yrs_in_office = 1  # reset to year 1
        party_office_list.append(party_yrs_in_office)   # append the year number

    # Create the dataframe 'plotframe' that will be used to create the bokeh graph
    plotframe = pd.DataFrame({'foo': []})
    plotframe['Total Change'] = total_chg
    plotframe['Percent Change'] = cov_list
    plotframe['Years'] = years_list
    plotframe['Party'] = party_list
    plotframe['First Executive'] = fe_list
    plotframe['Years in Office'] = office_yr_list
    plotframe['Years Party in Office'] = party_office_list
    plotframe.set_index('foo', drop=True, inplace=True)  # remove stock column in a roundabout way
    plotframe.set_index('Years', drop=True, inplace=True)  # remove the year column and set as index
    grouped = plotframe.groupby('First Executive')

    # ''' Bokeh Plot ''' ''' -- soon to be converted to Plotly Javascript --
    p = plotting.figure(title=title,
               x_axis_label=x_lb,
               y_axis_label='Percent Change in ' + y_lb,
               tools="pan,box_zoom,reset,save",
               toolbar_location='below',
               toolbar_sticky=False,
               plot_height= 800,
               plot_width= 800

               )
    # use the plasma palette from bokeh using the number of lines in the figure to create a palette from plasma256
    palette = [palettes.viridis(len(grouped))[i] for i, _ in enumerate(grouped)]
    for idx, (name, data) in enumerate(grouped):
        p.line(x=data['Years in Office'],
               y=data['Percent Change'],
               color=palette[idx],
               legend=name,
               )
    p.background_fill_color = "LightGrey"
    script, div = components(p)  # split the graph into JSON/JS components script and div
    # '''            ''' ''' -- soon to be converted to Plotly Javascript --

    # convert the datframe to html for easy display
    df_htmltable = plotframe.to_html(bold_rows=True, escape=True, classes='dftable')
    if render:
        # If rendering, display the web page
        plotting.show(p)
        return render_template(html, script=script, div=div, table=df_htmltable, var=urlth)

    else:
        # otherwise, return the result dataframe and the input dataframe
        return {'plotframe': plotframe, 'input_frame': df1}
