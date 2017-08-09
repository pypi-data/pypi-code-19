from ClearBladeCore import System, Query, Developer
import cbLogs
import json
# import random
# import time
# import Messaging

cbLogs.DEBUG = True
cbLogs.MQTT_DEBUG = True

# System 1
# postgres db
key = "8e88cf920be8c8b49ff28caec245"
secret = "8E88CF920BA6FDE3BFD9F6B5BB9C01"
# sqlite db
# key = "caa0c3930b9affa09382b7e8a89d01"
# secret = "CAA0C3930BA4EECCB8ADF3F0A3F901"
# url = "https://staging.clearblade.com"
url = "http://localhost:9000"

# System 1 collection
colID = "e0b0e2920bfec2e1e0a2ffa6ce10"

# System 2
key2 = "da95cf920bcee2c59af1a6b3f1cd01"
secret2 = "DA95CF920BCC93D990E191E5E474"

# User 1
email = "cbman@clearblade.com"
password = "cbpass"
passwordalt = "clearblade"

# User 2
email2 = "mpandola@clearblade.com"
password2 = "cbpass"

cb = System(key, secret, url)
yo = cb.User(email, password)

a = cb.Device("NewDevice", "yo")
b = cb.getDevices()
print(a.headers)
print(b)

quit()

dev = Developer(email, passwordalt, url)

q = Query()
q.equalTo("name", "sensorA")
q.greaterThan("temp", 80)

q2 = Query()
q2.lessThanEqualTo("temp", 60)

# for i in range(20, 1000):
#     name = "test" + str(i)
#     dev.newDevice(cb, name)
#     dev.updateDevice(cb, name, {"type": "test"})
#     dev.deleteDevice(cb, name)

# resp = dev.newDevice(cb, "test11")
# print(resp
exit()
user = cb.User(email, "yo")
# # anon = cb.AnonUser()
# print(user.headers
# # print(anon.headers
# test = cb.getDevice(user, "test11")
# col = cb.Collection(user, collectionName="yoo")

# q = Query()
# q.equalTo("beep", "bloop")

# col.deleteItems(q)

# for item in col.items:
#     print(item
# resp = Devices.getDevices(user)

yo = cb.Service("yo")
yo.execute(user, json.dumps({"key": "val"}))

# resp = cb.newDevice(user, "test10")
exit()

device = cb.Device("test", key="abc")
device.update(json.dumps({"enabled": True}))

exit()

# a = Devices.Device(cb, "NewDevice", "yo")
# a.authorize("yo")
# print(a.headers

m = cb.Messaging(device)


def yo2(client, userdata, flags, rc):
    print("connected")


def yo(client, userdata, message):
    a = int(message.payload)
    if a % 1000 == 0:
        print(str(a))
    a = str(a + 1)
    client.publish(message.topic, a)


def letsgetitstarted(client, userdata, mid, granted_qos):
    client.publish("stress_test", "1")


# m.on_message = yo

m.on_connect = yo2

# m.on_subscribe = letsgetitstarted

m.connect()

m.subscribe("stress_test")

# time.sleep(30)

m.disconnect()

anon = cb.AnonUser()

# newUser = cb.registerUser(device, email2, password2)

dev = cb.DevUser(email, passwordalt)

col = cb.Collection(device, colID)

# Get all rows where: (name="sensorA" AND temp>80) OR temp<=60

'''
[
    [
        {"EQ": [
            {"name": "sensorA"}
        ]},
        {"GT":[
            {"temp": 80}
        ]}
    ],
    [
        {"LTE": [
            {"temp": 60}
        ]}
    ]
]
'''

q = Query()
q.equalTo("name", "sensorA")
q.greaterThan("temp", 80)

q2 = Query()
q2.lessThanEqualTo("temp", 60)

col.getItems(q.Or(q2))

newTemp = {
    "temp": 84
}
q_up = Query()
q_up.equalTo("item_id", "d4b062a0-3835-4abc-ab14-817935343dd5")
col.updateItems(q_up, newTemp)

print(cb.collections)
print(col.items)

# for item in col.items:
#     print(item


# for i in range(65,91):

#     data = {
#         "name": "sensor"+chr(i),
#         "temp": random.randint(60,69)
#     }

#     resp = col.createItem(data)


# print(user.token
# print(user2.token
# print(anon.token
# print(dev.token
# if newUser is not None:
#     print(newUser.token
