import datetime
import time


class DatetimePlus(object):
    #字符串格式化成时间
    @classmethod
    def strToDateTime(cls,datetimeStr):
        result = datetime.datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S')
        return result

    #取当前时间格式化成字符串用作SQL
    @classmethod
    def getNowToStr(cls):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    #时间格式化成字符串可以用作SQL
    @classmethod
    def datetimeToStr(cls,timeValue):
        return timeValue.strftime('%Y-%m-%d %H:%M:%S')

    #取当前日期并格式化
    @classmethod
    def getNowDateToStr(cls):
        result = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        return result

    #取当前时间格式化为文件名使用
    @classmethod
    def getNowTimeToFileName(cls):
        result = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        return result

    #加秒
    @classmethod
    def addSeconds(cls,sourceTime,second):
        curTime = datetime.timedelta(seconds=second)
        result = sourceTime + curTime
        return result

    #取当前时间
    @classmethod
    def getNow(cls):
        return datetime.datetime.now()

    #获取两个时间相差的秒数
    @classmethod
    def diffSeconds(cls,t1,t2):
        return (t1 - t2).seconds

