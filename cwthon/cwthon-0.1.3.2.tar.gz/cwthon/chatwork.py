# -*- coding: utf-8 -*-
import logging
import requests
from requests import Response
import datetime
from cwthon import _util, _base
from cwthon.chatwork_prop import *

contactDict = _base.updateContactDictCache()
roomDict = _base.updateRoomDictCache()

def getContactInfo(account_id : int) -> dict:
    '''
    コンタクト情報を取得する。
    キャッシュ上に引数のアカウントIDのコンタクト情報が存在しない場合、APIから再取得を行う。
    アカウントIDのコンタクト情報が存在しない場合、Noneを返す
    :param account_id: チャットワークのアカウントID
    :return: アカウント情報
    '''
    contactInfo = contactDict.get(int(account_id))
    if contactInfo is None :
        contactDict.update(_base.updateContactDictCache())
        contactInfo = contactDict.get(int(account_id))
    return contactInfo

def getRoomInfo(room_id : int) -> dict:
    '''
    チャットルーム情報を取得する。
    キャッシュ上に引数のアカウントIDのチャットルーム情報が存在しない場合、APIから再読込を行う。
    ルームIDに紐づくチャットルームが存在しない場合、Noneを返す
    :param room_id: チャットルームID
    :return: チャットルーム情報
    '''
    roomInfo = roomDict.get(int(room_id))
    if roomInfo is None :
        roomDict.update(_base.updateRoomDictCache())
        roomInfo = roomDict.get(int(room_id))
    return roomInfo

class cwReq(object):
    '''
    メッセージ送信を行うクラス。
    '''
    __endPoint = None
    __params = None
    def sendMsgToAccount(self, account_id : int, msg : str):
        self.__endPoint = cwEndPoint.SEND_MSG
        self.__params = getContactInfo(account_id)
        self.__params.update({'body' : msg})
        return self.__send()

    def sendMsgToRoom(self, room_id : int, msg : str):
        self.__endPoint = cwEndPoint.SEND_MSG
        self.__params = getRoomInfo(room_id)
        self.__params.update({'body' : msg})
        return self.__send()

    def __send(self):
        method = self.__endPoint.value['method']
        if method is None :
            logging.error("cwReq cant send. method was None")
            return

        endPointUrl = self.__getEndPointUrl()

        res = None

        if method is reqMethods.POST:
            res = requests.post(
                url=endPointUrl,
                headers=_base.reqHdr,
                data={'body' : self.__params['body']}
                )
        elif method is reqMethods.GET:
            logging.error('send GET req Not implemented')
        elif method is reqMethods.DELETE:
            logging.error('send DELTE req is Not implemented')
        
        return cwRes(res)

    def __getEndPointUrl(self) -> str:
        path = _util.replaceParam(
            target = self.__endPoint.value['url'],
            params = self.__params)
        return _base.baseUrl + path

class cwRes:
    '''
    APIにリクエスト送信後の、レスポンス情報を格納するクラス。
    '''
    isErr = False
    def __init__(self, res : Response):
        self.res : Response = res
        if res.status_code is not 200 :
            self.isErr = True
            return

        self.limit : int = res.headers.get('X-RateLimit-Limit')
        self.remaining : int = res.headers.get('X-RateLimit-Remaining')
        self.reset : datetime = None
        resetUnix = res.headers.get('X-RateLimit-Reset')
        if resetUnix is not None :
            self.reset = datetime.datetime.fromtimestamp(int(resetUnix))