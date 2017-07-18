import json

import requests
from utils import checkIfCommitExists

TOKEN = '5326992d9d948cbfb0bf5be8f2964d42'
headers = {'X-TrackerToken': TOKEN}
payload = {'limit':500}    #Default Params for Stories

def getStoriesByState (project_id, payload, headers):
    story_type = ['feature', 'bug']
    state = ['accepted', 'delivered', 'finished']
    tempDictionary = []
    for j in range (0, 2):
        payload['with_story_type']=story_type[j]
        for i in range (0, 3):
            payload['with_state']=state [i]
            tempDictionary.extend(getAllStoriesAsDictionary(project_id, payload, headers))
    return tempDictionary

def getAllStoriesAsDictionary (project_id, payload, headers):
    tempDictionary = []
    counter = 0
    while (len (tempDictionary) % 500 == 0):
        offset = counter * 500
        payload['offset'] = offset
        r = requests.get('https://www.pivotaltracker.com/services/v5/projects/{}/stories'.format(project_id),
                     params=payload, headers=headers)
        response = r.json()
        stringResponse = json.dumps(response, sort_keys=True, indent=2, separators=(',', ': '))
        iterationDictionary = json.loads(stringResponse)
        if (len (iterationDictionary) == 0):
            break
        tempDictionary.extend(iterationDictionary)
        counter = counter + 1
    return tempDictionary

def getComments (project_id, headers, story):
    r = requests.get('https://www.pivotaltracker.com/services/v5/projects/{}/stories/{}/comments'.
                         format(project_id, story['id']), headers=headers)
    formattedCommentList = []
    if (r.status_code != 404):
        response = r.json()
        stringResponse = json.dumps(response, sort_keys=True, indent=2, separators=(',', ': '))
        formattedCommentList = json.loads(stringResponse)
    return (formattedCommentList)

def getCommits (story, shaDict, repoDict):   #Get all valid commits by cross checking with entire git repo
    commentDictionary = story['comments']
    story['commit_identifier'] = list()
    story['commiter'] = list()
    story['test'] = 'No'
    story['date'] = 'N/A'
    filesChanged = []

    for j in range(0, len(commentDictionary)):
        if ('commit_identifier' in commentDictionary[j]):
            sha1 = commentDictionary[j]['commit_identifier']
            for repo in repoDict:
                sha1List = shaDict[repo]
                if (checkIfCommitExists(sha1, sha1List)):
                    commitInfo = repoDict[repo].git.show(sha1,name_only=True).splitlines()  # use gitpython to get commit data
                    story['commit_identifier'].append(sha1)  # requires local clone
                    for k in range(0, len(commitInfo)):  # For each line in the commit data
                        commitString = commitInfo[k]
                        if ('/' in commitString and story['story_type'] == 'bug'):  # Line in commit refers to a file
                            if not (' ' in commitString):  # If the string contains spaces it is not a file
                                file_paths = commitString.split('/')
                                filesChanged.append(file_paths[len(file_paths) - 1])
                        if ('author' in commitString.lower()):
                            if not (commitString.lower() in story['commiter']):  # Refers to user
                                story['commiter'].append(commitString.lower())
                        if ('test' in commitString.lower()):    # If Test File is referenced
                            if not (' ') in commitString.strip():
                                story['test'] = 'Yes'
                        if ('Date' in commitString and story['date'] == 'N/A'):
                            story['date'] = commitString
    if (filesChanged != []):
        story['files_changed'] = filesChanged

def getParsedStories (project_id, sha1Dict, repoDict, date):
    if (date != None):
        dateTime = '%sT00:00:00Z' % date
        payload['created_after'] = dateTime
    storyDictionary = getStoriesByState(project_id, payload, headers)
    totalStories = (len(storyDictionary))
    print ('%s stories,' % totalStories),
    for i in range(0, totalStories):
        storyDictionary [i]['comments'] = getComments (project_id, headers, storyDictionary[i])
        getCommits(storyDictionary[i], sha1Dict, repoDict)
    return storyDictionary