#! python3

import urllib.request
import re
import sys
import os
import progressbar

from apiclient.discovery import build
from apiclient.errors import HttpError
import argparse

DEVELOPER_KEY = 'AIzaSyAdlu2o-qmh6wKHN26uSJci7gzxlLzeD0I'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
DOWNLOADS_FOLDER_PATH = os.path.join(os.getcwd(), "downloads")

Progressbar = None
Downloaded = 0
Done = False

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    print(chr(27) + "[2J") # Clear terminalscreen

    # Parse given arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", help="Search term", default=None)
    parser.add_argument("--max-results", help="Max results", default=1)
    parser.add_argument("--list", help="Txt file with video titles to download", default=None)
    args = parser.parse_args()

    # Start main functionality
    try:
        youtube_search(args)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

def slugify(value):
    value = str(value).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', value)

def progress(count, blockSize, totalSize):
    global Progressbar, Downloaded, Done

    if totalSize <= 0:
        raise Exception('totalSize < 0')

    if Progressbar is None and Done is False:
        Progressbar = progressbar.ProgressBar(max_value=totalSize)

    Downloaded = Downloaded + blockSize
    if Downloaded > totalSize:
        Downloaded = totalSize

    if Downloaded >= totalSize:
        Progressbar.finish()
        Progressbar = None
        Downloaded = 0
        Done = True
    if Done is False:
        Progressbar.update(Downloaded)

def download_video(video_url, video_name):
    url = "http://www.youtubeinmp3.com/fetch/?video=%s" % video_url
    file_name = slugify(video_name + ".mp3")
    urllib.request.urlretrieve(url, file_name, progress)
    print("")
    return file_name

def youtube_search(options):
    global Done
    print("Creating YoutubeAPI connection...")
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    videos = []
    if options.q != None:
        videos.append(options.q)
    if options.list != None:
        file = open(options.list)
        videos = file.readlines()
    if len(videos) == 0:
        print("No video titles supplied!")
        return

    list_watcher = list(videos)
    failed_videos = []

    for old_title in videos:
        raw_old_title = old_title
        old_title = old_title.rstrip()
        Done = False
        print("Looking for video containing '%s'..." % old_title)
        search_response = youtube.search().list(
            q=old_title,
            part='id,snippet',
            maxResults=options.max_results
        ).execute()

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                title = search_result['snippet']['title']
                url = ("https://www.youtube.com/watch?v=%s" % search_result['id']['videoId'])
                print("Found video: %s" % title)

                print("Starting download...")
                try:
                    file_name = download_video(url, title)
                    print("Done downloading: %s" % title)
                    print("Saved as: %s" % os.path.join(DOWNLOADS_FOLDER_PATH, file_name))
                    list_watcher.remove(raw_old_title)
                    file = open(options.list, "w")
                    file.writelines(list_watcher)
                    if len(videos) > 1: print("Removed '%s' from the list" % old_title)
                    if len(videos) > 1: print("------------------------------------")
                except Exception as e:
                    print("Something went wrong while downloading the video:\n%s" % repr(e))
                    failed_videos.append(raw_old_title)
                    file = open("failed_videos.txt","w")
                    file.writelines(failed_videos)
                    print("Saved video in 'failed_videos.txt'")
                    if len(videos) > 1: print("------------------------------------")

if __name__ == "__main__":
    main() # Can not have args, because of entry_points