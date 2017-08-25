# -*- coding: utf-8 -*-
'''
  track_grabber
    Created by: Jospeh Jones

  Purpose:
    Have you ever wanted to find some popular songs from a new artist you found out about?
    Did you think it was tedious typing searches into google and finding the songs on youtube?
    This is the script for you, it generates an HTML page with the most popular songs found on
    Last.FM. On this list you will find the song names and a link to the youtube video.
'''
import os               # Get current directory
import argparse         # Handle arguments
import codecs           # Handle utf8 with files
import requests         # HTTP requests
from bs4 import BeautifulSoup   # Easily find information in html
from tqdm import tqdm           # Progress bar

# TODO: Speed up generating the html page (Probably the requests to youtube)
# TODO: Encapsulate for easier maintainability


def main():
    ''' Main '''
    # Get artist name from arguments
    parser = argparse.ArgumentParser(
        description="Grab list of tracks of a music artist from Last.FM")
    parser.add_argument("artist", type=str, nargs=1, help="Artist's name")
    args = parser.parse_args()
    get_tracks(args.artist)


def get_tracks(artist):
    ''' Get tracks from Last.FM '''
    # Open tracks page of artist on Last.FM
    response = requests.get("https://www.last.fm/music/%s/+tracks" % artist[0])

    # Check if the artist exists on Last.FM
    if response.status_code == 200:
        html = response.text
        # Give the html response to beautiful soup
        soup = BeautifulSoup(html, "html.parser")

        # Find the titles of the songs
        links = soup.findAll(attrs={'class': 'chartlist-name'})
        titles = []
        for link in links:
            titles.append(link.a["title"])

        # Check if we found any titles
        if len(titles) > 0:
            generate_page(artist, titles)
        else:
            print("No tracks found for '%s' not found..." % artist[0])
    else:
        print("'%s' not found..." % artist[0])


def generate_page(artist, titles):
    ''' Generate a html page to easily find any songs you want on youtube '''
    # Create boilerplate html for a good looking site
    head_boilerplate = '''<html><head><title>%s - Tracks</title>
    <link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css\" integrity=\"sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M\" crossorigin=\"anonymous\">
    </head><body><div class=\"container-fluid\"><div class="row justify-content-center"><h2>%s - Tracks</h2></div>
    <table class=\"table\"><thead class=\"thead-default\">
    <tr><th>Track Name</th><th>Youtube Link</th></tr></thead><tbody>''' % (artist[0], artist[0])
    body = ""
    foot_boilerplate = '''</tbody></table></div><script src=\"https://code.jquery.com/jquery-3.2.1.slim.min.js\" integrity=\"sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN\" crossorigin=\"anonymous\"></script>
<script src=\"https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js\" integrity=\"sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4\" crossorigin=\"anonymous\"></script>
<script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/js/bootstrap.min.js\" integrity=\"sha384-h0AbiXch4ZDo7tp9hKZ4TsHbi047NrKGLO3SEJAg45jXxnGIfYzk4Si90RDIqNm1\" crossorigin=\"anonymous\"></script></body></html>'''

    print("This may take a minute...")

    # Add a row in the table for each track
    for title in tqdm(titles):
        # Create query for youtube
        url = "https://www.youtube.com/results?search_query=%s+%s" % (title, artist[0])

        try:
            response = requests.get(url)
        except UnicodeEncodeError:
            print("Sorry, can't search for %s" % title)

        html = response.text
        # Give the html response to beautiful soup
        soup = BeautifulSoup(html, "html.parser")
        try:
            # Parse html to find references to videos and get the first one
            vid_url = "https://www.youtube.com%s" % soup.find(
                attrs={'class': 'yt-uix-tile-link'})["href"]
        except TypeError:
            # No videos found
            print("Sorry, could not find any youtube videos for %s" % title)

        link = "<a href=\"%s\">LINK</a>" % vid_url
        body += "<tr><td>%s</td><td>%s</td></tr>" % (title, link)

    # Create the html file with the given boilerplate and table
    with codecs.open("tracks_%s.html" % (artist[0].replace(' ', '+')), "w", "utf-8") as f:
        f.write(head_boilerplate)
        f.write(body)
        f.write(foot_boilerplate)

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    print("tracks_%s.html created in %s" % (artist[0].replace(' ', '+'), cur_dir))

main()
