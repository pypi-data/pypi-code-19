from csvhelper import insertStories
from csvhelper import insertTestData
from csvhelper import insertTopFiles
from csvhelper import trackTopFiles

from trackerhelper import getParsedStories
from utils import checkDate
from utils import findTests
from utils import findTopFiles
from utils import getSha1List
from utils import initRepo
from utils import parseFiles
from utils import parseTests

import os

repoDict = {}
sha1Dict = {}

def getData (project_id, date):
    return getParsedStories(project_id, sha1Dict, repoDict, date)

def getRepos (USER_WORKSPACE, repositories):
    for i in range(0, len(repositories)):
        project_path = USER_WORKSPACE % repositories[i]
        repoDict[repositories[i]] = (initRepo(project_path))
        repoDict[repositories[i]].config_reader()
        sha1Dict[repositories[i]] = getSha1List(repoDict[repositories[i]])

def main (USER_WORKSPACE, project_id, repositories):
    #project_id = 1909305
    #repositories = ['2017-07-01', 'bbm-a']
    date = None
    if checkDate (repositories[0]):
        date = repositories[0]
        repositories.remove(date)
    project_name = repositories[0]
    print ('Started %s,' % (project_name)),
    getRepos( USER_WORKSPACE + '/%s', repositories)

    storyDictionary = getData(project_id, date)  # Get Data from PivotalTracker
    testList = findTests(storyDictionary)
    fileList = parseFiles(storyDictionary)
    topFiles = findTopFiles(fileList)
    testData = parseTests(testList)

    file_path = USER_WORKSPACE + '/tracker_%s' % project_name
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    insertStories(file_path, storyDictionary)
    insertTestData(file_path, testData)
    insertTopFiles(file_path, topFiles)
    trend_path = USER_WORKSPACE + '/data_trends'
    trackTopFiles(trend_path, project_name, topFiles)
