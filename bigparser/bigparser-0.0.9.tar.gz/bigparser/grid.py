from bigparser.bigparser import bigparser
import numpy as np
import pandas as pd


class grid:
    prod_uri = "https://www.bigparser.com/APIServices/";
    qa_uri = "https://qa.bigparser.com/APIServices/";
    flag = 1
    uri = None
    if flag == 1:
        uri = prod_uri
    else:
        uri = qa_uri
    header_list = None
    authId = None
    limit = 100
    gridId = None
    count = None
    curated_header = None

    def __init__(self, authId, gridId, limit=None):
        self.authId = authId
        self.gridId = gridId
        if limit is not None:
            self.limit = limit

    def getRows(self, searchfilter=None, sort=None, columns=None, dataframe=None):
        sortKeys = list()
        tags = list()
        keywords = list()
        selectColumnsStoreName = None
        grid.getHeaders(self)
        if self.limit is not None:
            rowCount = self.limit
        else:
            rowCount = 10
        if searchfilter is not None:
            if "GLOBAL" in searchfilter.keys():
                GLOBAL = searchfilter['GLOBAL']
                keywords = GLOBAL
            for item in searchfilter:
                if item != "GLOBAL":
                    for a in searchfilter[item]:
                        temp = dict()
                        temp['columnValue'] = a
                        temp['columnStoreName'] = self.header_list[item]
                        tags.append(temp)
        if sort is not None:
            for item in sort:
                for key in item:
                    tempDict = dict()
                    tempDict['columnStoreName'] = self.header_list[key]
                    if item[key] == "ASC":
                        tempDict['ascending'] = 'true'
                    else:
                        tempDict['ascending'] = 'false'
                sortKeys.append(tempDict)
        if columns is not None:
            selectColumnsStoreName = list()
            for item in columns:
                for columnName, id in self.header_list.items():
                    if item == columnName:
                        selectColumnsStoreName.append(id)
        if columns is not None:
            self.curated_header = [item.upper() for item in columns]
        else:
            self.curated_header = [item.upper() for item in self.header_list.keys()]
        if searchfilter and sort is None and columns is None:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords, tags=tags)
        elif searchfilter is None and sort is not None and columns is None:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords, sortKeys=sortKeys)
        elif searchfilter is None and sort is None and columns:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords, selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter and sort and columns is None:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords, tags=tags, sortKeys=sortKeys)
        elif searchfilter and sort is None and columns:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords, tags=tags,
                                         selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter is None and sortKeys and columns:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords, sortKeys=sortKeys,
                                         selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter and sort and columns:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords, tags=tags, sortKeys=sortKeys,
                                         selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter is None and sort is None and columns is None:
            response = bigparser.getData(self.authId, self.gridId, rowCount=rowCount, keywords=keywords)
        records = list()
        try:
            for data in response['rows']:
                records.append(data['data'])
            return records
        except KeyError:
            return "Your search query did not return any results"

    def getHeaders(self):
        response = bigparser.getHeader(self.authId, self.gridId)
        self.header_list = response['columns']
        tempDict = dict()
        count = 0
        for item in self.header_list:
            tempDict[str(item['columnName']).lower()] = count
            count = count + 1
        self.header_list = tempDict
        return tempDict

    def getLastRow(self, count=None, searchfilter=None, sort=None, columns=None):
        sortKeys = list()
        tags = list()
        keywords = list()
        selectColumnsStoreName = None
        grid.getHeaders(self)
        if self.limit is not None:
            rowCount = self.limit
        else:
            rowCount = 10
        if searchfilter is not None:
            if "GLOBAL" in searchfilter.keys():
                GLOBAL = searchfilter['GLOBAL']
                keywords = GLOBAL
            for item in searchfilter:
                if item != "GLOBAL":
                    for a in searchfilter[item]:
                        temp = dict()
                        temp['columnValue'] = a
                        temp['columnStoreName'] = self.header_list[item]
                        tags.append(temp)
        if sort is not None:
            for item in sort:
                for key in item:
                    tempDict = dict()
                    tempDict['columnStoreName'] = self.header_list[key]
                    if item[key] == "ASC":
                        tempDict['ascending'] = 'true'
                    else:
                        tempDict['ascending'] = 'false'
                sortKeys.append(tempDict)
        if columns is not None:
            selectColumnsStoreName = list()
            for item in columns:
                for columnName, id in self.header_list.items():
                    if item == columnName:
                        selectColumnsStoreName.append(id)
        if columns is not None:
            self.curated_header = [item.upper() for item in columns]
        else:
            self.curated_header = [item.upper() for item in self.header_list.keys()]
        if searchfilter and sort is None and columns is None:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords, tags=tags)
        elif searchfilter is None and sort is not None and columns is None:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords, sortKeys=sortKeys)
        elif searchfilter is None and sort is None and columns:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords, selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter and sort and columns is None:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords, tags=tags, sortKeys=sortKeys)
        elif searchfilter and sort is None and columns:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords, tags=tags,
                                         selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter is None and sortKeys and columns:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords, sortKeys=sortKeys,
                                         selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter and sort and columns:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords, tags=tags, sortKeys=sortKeys,
                                         selectColumnsStoreName=selectColumnsStoreName)
        elif searchfilter is None and sort is None and columns is None:
            response = bigparser.getLastRow(self.authId, self.gridId,count=count, rowCount=rowCount, keywords=keywords)
        records = list()
        try:
            for data in response['rows']:
                records.append(data['data'])
            return records
        except KeyError:
            return "Your search query did not return any results"
        # if type(response) == "<class 'str'>":
        #     return response
        # if count is None:
        #     return response[-1:]
        # else:
        #     return response[-count:]

    def getRange(self, rows, columns):
        response = grid.getRows(self, dataframe=False)
        # records = list()
        # for data in response['rows']:
        #     records.append(data['data'])
        df = pd.DataFrame(np.array(response), columns=self.curated_header)
        temp = df.iloc[0:rows, 0:columns]
        return temp
