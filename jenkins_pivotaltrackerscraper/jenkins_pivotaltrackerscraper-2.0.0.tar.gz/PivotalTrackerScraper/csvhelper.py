import csv
import os.path
from utils import prepStory

def insertTestData (ROOT_DIR, test_data):
    TEST_PATH = ROOT_DIR + '/test_data.csv'
    TEST_HEADERS = ['WITH TEST', 'WITHOUT TEST', 'UNIT TEST COVERAGE PERCENTAGE']
    if not (os.path.isfile(TEST_PATH)):
        with open(TEST_PATH, 'w') as test_file:
            wr = csv.writer(test_file, quoting=csv.QUOTE_ALL)
            wr.writerow(TEST_HEADERS)
    TEST_PERCENTAGE = round((float (test_data['Yes'])/test_data['Total']) * 100,2)
    TEST_DATA = [test_data['Yes'], test_data['No'], TEST_PERCENTAGE]
    with open(TEST_PATH, 'a') as test_file:
        wr = csv.writer(test_file, quoting=csv.QUOTE_ALL)
        wr.writerow(TEST_DATA)

def insertTopFiles (ROOT_DIR, top_files):
    FILES_PATH = ROOT_DIR + '/top_files.csv'
    FILES_HEADERS = []
    FILE_ROW = []
    for file in top_files:
        FILES_HEADERS.append(file)
        FILE_ROW.append(top_files[file])
    with open(FILES_PATH, 'w') as top_file:
        wr = csv.writer(top_file, quoting=csv.QUOTE_ALL)
        wr.writerow(FILES_HEADERS)
        wr.writerow(FILE_ROW)

def trackTopFiles (ROOT_DIR, project_name, top_files_counter):
    FILES_PATH = ROOT_DIR + '/files_trend_%s.csv' % project_name
    FILES_HEADERS = []
    FILE_ROW = []
    if not (os.path.isfile(FILES_PATH)):
        for file in top_files_counter:
            FILES_HEADERS.insert(0, len(FILES_HEADERS)/2)
            FILE_ROW.append(top_files_counter[file])
            FILE_ROW.insert(0, 0)
            FILES_HEADERS.append(file)
        with open(FILES_PATH, 'w') as file_trend:
            wr = csv.writer(file_trend, quoting=csv.QUOTE_ALL)
            wr.writerow(FILES_HEADERS)
            wr.writerow(FILE_ROW)
    else:
        with open (FILES_PATH, 'rb') as file_trend:
            reader = csv.reader(file_trend)
            row_list = list(reader)
            previous_files = row_list[0]
            previous_count = row_list[1]
            for file in top_files_counter:
                if (file in previous_files):
                    index = previous_files.index(file)
                    previous_count[index] = top_files_counter[file]
                else:
                    previous_files.insert(0, len(previous_files)/2)
                    previous_count.insert(0, 0)
                    previous_files.append(file)
                    previous_count.append(top_files_counter[file])
        with open(FILES_PATH, 'w') as file_trend:
            wr = csv.writer(file_trend, quoting=csv.QUOTE_ALL)
            wr.writerow(previous_files)
            wr.writerow(previous_count)

def insertStories (ROOT_DIR, stories):
    STORY_PATH = ROOT_DIR + '/all_stories.csv'
    STORY_HEADERS = ['URL', 'TITLE', 'TYPE', 'DATE', 'COMMIT ID', 'FILES_CHANGED', 'TEST', 'OWNER']
    with open(STORY_PATH, 'w') as stories_file:
        wr = csv.writer(stories_file, quoting=csv.QUOTE_ALL)
        wr.writerow(STORY_HEADERS)
        for i in range(0, len(stories)):
            story = prepStory(stories [i])
            if not (story == []):
                encoded_story = [text.encode("utf8") for text in story]
                wr.writerow(encoded_story)
