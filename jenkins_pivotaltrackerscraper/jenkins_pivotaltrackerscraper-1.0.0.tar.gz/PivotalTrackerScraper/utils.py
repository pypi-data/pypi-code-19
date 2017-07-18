from git import Repo
import calendar
import datetime
abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}

def checkIfCommitExists (sha1, sha1List):
    return sha1 in sha1List

def getSha1List (repo): #Gets all commits in repo
    sha1List = []
    for git_commit in repo.iter_commits():
        sha1List.append(git_commit.hexsha)
    return sha1List

def initRepo (uri):
    repo = Repo(uri)
    assert not repo.bare
    return repo

def trimAuthor (owner):
    return owner[8:]

def trimDate (date):
    if not 'N/A' in date:
        parts = date.split()
        month = abbr_to_num[parts[2]]
        return '%s/%s/%s' % (parts[5], month, parts[3])
    return date

def prepStory (dictionary):
    url = dictionary['url']
    title = dictionary['name']
    type = dictionary['story_type']
    date = trimDate(dictionary['date'])
    owner = 'N/A'
    commitID = 'No commit yet'
    filesChanged = ''
    if (dictionary ['commiter'] != []):
        owner = trimAuthor(dictionary['commiter'][0])
        for j in range (1, len(dictionary['commiter'])):
            owner += '\n' + dictionary['commiter'][j]
    if (dictionary ['commit_identifier'] != []):
        commitID = dictionary['commit_identifier'][0]
        for j in range (1, len(dictionary['commit_identifier'])):
            commitID += '\n' + dictionary['commit_identifier'][j]
    if ('files_changed' in dictionary):
        filesChanged = dictionary['files_changed'][0]
        for j in range(1, len(dictionary['files_changed'])):
            filesChanged += '\n' + dictionary['files_changed'][j]
    test = dictionary['test']
    if ('No commit yet' in commitID):
        return []
    return [url, title, type, date, commitID, filesChanged, test, owner]

def setValues (storyDictionary):
    finalValues = []
    for i in range (0, len(storyDictionary)):
        dictionary = storyDictionary[i]
        values = prepStory(dictionary)
        if (values != []):
            finalValues.append(values)
    return finalValues

def parseFiles (rawData):
    fileList = {}
    for i in range(0, len(rawData)):
        if ('files_changed' in rawData[i]):
            files = rawData[i]['files_changed']
            for j in range(0, len(files)):
                if (fileList.has_key(files[j]) == False):
                    fileList[files[j]] = 1
                else:
                    fileList[files[j]] = fileList[files[j]] + 1
    return fileList

def commandLineID ():
    return raw_input ('Project id: ')

def commandLineRepo ():
    input = raw_input('Repos: ')
    list = input.split(' ')
    repoList = []
    for i in range (0, len(list)):
        repoList.insert(i, list[i])
    return repoList

def findTests (rawData):
    testList = []
    for i in range (0, len(rawData)):
        if not (rawData[i]['commit_identifier'] == []):
            testList.append(rawData[i]['test'])
    return testList

def parseTests (test_list):
    tests = {'Yes': 0, 'No': 0, 'Total': 0}
    for i in range (0 , len(test_list)):
        if ('Yes') in test_list[i]:
            tests ['Yes'] = tests ['Yes'] + 1
        else:
            tests ['No'] = tests ['No'] + 1
        tests ['Total'] = tests ['Total'] + 1
    return tests

def checkDate (date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        pass
    return False

def findTopFiles (file_list):
    topFiles = {}
    for file in sorted(file_list, key=file_list.get, reverse=True):
        if (len(topFiles) < 5):
            topFiles[(file)] = file_list[file]
        else:
            break
    return topFiles

def convertListToString (list):
    returnString = ''
    for i in range (0, len(list)):
        returnString = returnString + '\n' + list[i]
    return returnString