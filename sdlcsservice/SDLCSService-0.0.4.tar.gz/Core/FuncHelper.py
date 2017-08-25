
import json
import os

class FuncHelper(object):
    #字典转JSON
    @classmethod
    def dictToJson(cls,dValue,ensure_ascii=False):
        return json.dumps(dValue,ensure_ascii=False)

    #JSON转字典
    @classmethod
    def jsonToDict(cls,jValue):
        return json.loads(jValue)
    #创建目录树
    @classmethod
    def createDirs(cls,directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    #从URL返回文件名
    @classmethod
    def getFileNameByUrl(cls,url=''):
        i = url.rfind('/') + 1
        return url[i:]

    #获取扩展名
    @classmethod
    def getFileExtName(cls,s=''):
        i = s.rfind('.') + 1
        return s[i:]

    #返回程序根目录
    @classmethod
    def getCurrPath(cls):
        return os.getcwd()

    #字典转实例 用于向JS中访问JSON那样用.方法
    @classmethod
    def dictToInstance(cls,data):
        if not isinstance(data,dict):
            return None
        result = type('myInstance',(),data)
        for key in data.keys():
            if isinstance(data[key],dict):
                setattr(result,key,cls.dictToInstance(data[key]))
            elif isinstance(data[key],list):
                for i,d in enumerate(data[key]):
                    if isinstance(d,dict):
                        data[key][i] = cls.dictToInstance(d)
        return result

    # JSON转实例 用于向JS中访问JSON那样用.方法
    @classmethod
    def jsonToInstance(cls,jsonValue):
        jsonDict = cls.jsonToDict(jsonValue)
        return cls.dictToInstance(jsonDict)

if __name__ == '__main__':
    # print( FuncHelper.getFileNameByUrl('http://www.evun.cc/adfklsdfjsdf/sdf/123456789.zip'))
    # print(FuncHelper.getCurrPath())
    pass


