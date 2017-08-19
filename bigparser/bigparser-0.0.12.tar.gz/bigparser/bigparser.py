import requests
import json
import sys

'''
BpData This class implements the methods needed to connect to BigParser's
API to authenticate and fetch the required data
@author Ajay Arjun
@version 1.0
'''
prod_uri = "https://www.bigparser.com/APIServices/";
qa_uri = "https://qa.bigparser.com/APIServices/";

class bigparser:
    '''
    This method makes generic post calls
    @param endPointa
            Target URI
    @param headers
            Headers to be passed for the current request
    @param data
            Body of the post request
    @return String returns the response as JSON Object
    '''

    def __post(self, uri, headers, data):
        try:
            response = requests.post(uri, data=json.dumps(data), headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                if len(response.text):
                    responseData = json.loads(response.text)
                else:
                    return "200"
                return responseData
        except requests.exceptions.HTTPError as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)
        except requests.exceptions.Timeout as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)
        except requests.exceptions.ConnectionError as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)
        except requests.exceptions.RequestException as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)

    '''
    This method makes generic get calls
    @param endPoint 
            Target URI
    @param headers
            Headers to be passed for the current request
    @return String returns the response as JSON Object
    '''

    def __get(self, uri, headers):
        try:
            response = requests.get(uri, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                responseData = json.loads(response.text)
                return responseData
        except requests.exceptions.HTTPError as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)
        except requests.exceptions.Timeout as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)
        except requests.exceptions.ConnectionError as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)
        except requests.exceptions.RequestException as err:
            try:
                bigparser.throws(self,err.response.text)
                return 0
            except Exception as err:
                sys.stderr.write('ERROR: %sn' % str(err))
                exit(-1)

    def throws(self,message):
        raise RuntimeError(message)


    '''
    This method performs the task of login into BigParser account and fetch authId for future calls
    @param emailId
        emailId/username of your account
    @param password
        password to login into BigParser account
    @return String returns the response as JSON Object
    '''

    @classmethod
    def login(self, username, password):
        uri = "https://www.bigparser.com/APIServices/api/common/login"
        data = {'emailId': '' + username + '', 'password': '' + password + ''}
        headers = {'content-type': 'application/json'}
        response = bigparser.__post(self, uri, headers, data)
        authId = response["authId"]
        return authId

    '''
    This method performs the task of login into BigParser account and fetch authId for future calls
    @param emailId
        emailId/username of your account
    @param password
        password to login into BigParser account
    @return String returns the response as JSON Object
    '''

    @classmethod
    def signup(self, emailId, password, fullName, mobileNumber, srcName=None, visitId=None):
        uri = "https://www.bigparser.com/APIServices/api/common/signup"
        data = dict()
        data['emailId'] = emailId
        data['fullName'] = fullName
        data['password'] = password
        data['mobileNumber'] = mobileNumber
        if srcName is not None:
            data['srcName'] = srcName
        if visitId is not None:
            data['visitId'] = visitId
        print(data)
        headers = {'content-type': 'application/json'}
        response = bigparser.post(self, uri, headers, data)
        if response == "200":
            return "Please confirm your email address by signing in to your email to complete registration"
        return response

    '''
    Fetches rows from the specified grid. Parameters to query the grid are passed as a part of the post request
    @param emailId
        emailId/username of your account
    @param password
        password to login into BigParser account
    @param gridId
        gridId of the required grid
    @return String returns the response as JSON in string format
    '''

    @classmethod
    def getHeader(self, authId, gridId):
        uri = "https://www.bigparser.com/APIServices/api/grid/headers?gridId=" + gridId
        headers = {'content-type': 'application/json', 'authId': '' + authId + ''}
        response = bigparser.__get(self, uri, headers)
        return response

    '''
    Fetches rows from the specified grid. Parameters to query the grid are passed as a part of the post request
    @param emailId
        emailId/username of your account
    @param password
        password to login into BigParser account
    @param data
        comprises the options to query the grid in the form of JSON object.
    @return String returns the response as JSON in string format
    '''

    @classmethod
    def getData(self, authId, gridId, rowCount=50, selectColumnsStoreName=None, tags=None,
                keywords=None, sortKeys=None):
        uri = "https://www.bigparser.com/APIServices/api/query/table"
        headers = {'content-type': 'application/json', 'authId': '' + authId + ''}
        data = dict()
        data['gridId'] = gridId
        data['rowCount'] = rowCount
        if selectColumnsStoreName is not None:
            data['selectColumnsStoreName'] = selectColumnsStoreName
        if tags is not None:
            data['tags'] = tags
        if keywords is not None:
            data['keywords'] = keywords
        if sortKeys is not None:
            data['sortKeys'] = sortKeys
        response = bigparser.__post(self, uri, headers, data)
        return response

    '''
    Fetches rows from the specified grid. Parameters to query the grid are passed as a part of the post request
    @param emailId
        emailId/username of your account
    @param password
        password to login into BigParser account
    @param data
        comprises the options to query the grid in the form of JSON object.
    @return String returns the response as JSON in string format
    '''

    @classmethod
    def searchColumn(self, authId, gridId, columnStoreName, searchKey, pageSize):
        uri = "https://www.bigparser.com/APIServices/api/query/search"
        headers = {'content-type': 'application/json', 'authId': '' + authId + ''}
        data = dict()
        data['gridId'] = gridId
        data['columnStoreName'] = columnStoreName
        data['searchKey'] = searchKey
        data['pageSize'] = pageSize
        response = bigparser.post(self, uri, headers, data)
        return response

    @classmethod
    def getLastRow(self, authId, gridId,count=None, rowCount=50, selectColumnsStoreName=None, tags=None,
                keywords=None, sortKeys=None):
        uri = "https://www.bigparser.com/APIServices/api/query/table"
        headers = {'content-type': 'application/json', 'authId': '' + authId + ''}
        data = dict()
        data['gridId'] = gridId
        data['rowCount'] = rowCount
        if selectColumnsStoreName is not None:
            data['selectColumnsStoreName'] = selectColumnsStoreName
        if tags is not None:
            data['tags'] = tags
        if keywords is not None:
            data['keywords'] = keywords
        if sortKeys is not None:
            data['sortFields'] = sortKeys
        response = bigparser.__post(self,uri, headers, data)
        gridCount = response["count"]
        if count is None:
            uri = prod_uri + "api/query/table?startIndex=" + str(gridCount) + "&endIndex=" + str(gridCount)
        else:
            uri = prod_uri + "api/query/table?startIndex=" + str((gridCount-count)+1) + "&endIndex=" + str(gridCount)
        data.pop('rowCount',None)
        response = bigparser.__post(self, uri, headers, data)
        return response

    @classmethod
    def isFileExists(self, authId, filename):
        uri = "https://www.bigparser.com/APIServices/api/upload/isFileExisting"
        headers = {'content-type': 'application/json', 'authId': '' + authId + ''}
        data = dict()
        data['filename'] = [filename]
        response = bigparser.post(self, uri, headers, data)
        print(response)
