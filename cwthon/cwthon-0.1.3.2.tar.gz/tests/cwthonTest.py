import json
import requests
import datetime
from cwthon import chatwork, _base

if __name__ == '__main__':
    res : requests = requests.get(
        url='https://api.chatwork.com/v2/me',
        headers=_base.reqHdr)
    print(res.text)
    print(res.headers)
    myData= json.loads(res.text)
    print(datetime.datetime.fromtimestamp(int(res.headers.get('X-RateLimit-Reset'))))

    msgAc = 'test from account_id'
    account_id = myData['account_id']
    msgRo = 'test from room_id'
    room_id = myData['room_id']

    print("account_id[" + str(account_id) + "]")
    print("room_id[" + str(room_id) + "]")

    cwReq = chatwork.cwReq()
    cwRes : chatwork.cwRes = cwReq.sendMsgToRoom(room_id=room_id, msg=msgRo)
    print("limit = " + str(cwRes.limit))
    print("isErr = " + str(cwRes.isErr))
    print("remaining= " + str(cwRes.remaining))
    print("reset = " + str(cwRes.reset))