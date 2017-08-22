from csvhelper import writeStories
from csvhelper import writeTestData
from csvhelper import writeTopFiles
from csvhelper import trackTopFiles

from trackerhelper import getParsedStories
from utils import checkIfDateExists
from utils import findTests
from utils import findTopFiles
from utils import getSha1List
from utils import initRepo
from utils import parseFiles
from utils import parseTests

import os

repoDict = {}
sha1Dict = {}

def getData (TOKEN, project_id, date):
    return getParsedStories(TOKEN, project_id, sha1Dict, repoDict, date)

def getRepos (USER_WORKSPACE, repositories):
    for i in range(0, len(repositories)):
        project_path = USER_WORKSPACE % repositories[i]
        repoDict[repositories[i]] = (initRepo(project_path))
        repoDict[repositories[i]].config_reader()
        sha1Dict[repositories[i]] = getSha1List(repoDict[repositories[i]])

def run (TOKEN, USER_WORKSPACE, project_id, repositories):
    date = None
    if checkIfDateExists(repositories[0]):
        date = repositories[0]
        repositories.remove(date)
    project_name = repositories[0]
    print ('Started %s,' % (project_name)),
    getRepos( USER_WORKSPACE + '/%s', repositories)

    allStoriesDictionary = getData(TOKEN, project_id, date)  # Get Data from PivotalTracker
    testList = findTests(allStoriesDictionary)
    fileList = parseFiles(allStoriesDictionary)
    topFiles = findTopFiles(fileList)
    testData = parseTests(testList)

    file_path = USER_WORKSPACE + '/tracker_%s' % project_name
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    writeStories(file_path, allStoriesDictionary)
    writeTestData(file_path, testData)
    writeTopFiles(file_path, topFiles)
    trend_path = USER_WORKSPACE + '/data_trends'
    trackTopFiles(trend_path, project_name, topFiles)