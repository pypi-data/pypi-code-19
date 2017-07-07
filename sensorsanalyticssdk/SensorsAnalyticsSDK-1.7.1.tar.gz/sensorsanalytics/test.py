from sdk import *
import time

#TEST_DEBUG_URL_PREFIX = 'http://test-ckh-zyh.cloud.sensorsdata.cn:8006/sa?token=de28ecf691865360'

#SA_SERVER_URL = 'http://haomaiyi.cloud.sensorsdata.cn:8006/sa?token=1acabe930410bda8'
SA_SERVER_URL = 'http://10.10.36.102:8006/sa?token=de28ecf691865360'
SA_REQUEST_TIMEOUT = 1000
SA_BULK_SIZE = 1
consumer = ConsoleConsumer()
sa = SensorsAnalytics(consumer)
sa.track('100', 'submit')
sa.track('101', 'submit')
sa.flush()

# consumer = DebugConsumer(TEST_DEBUG_URL_PREFIX, True)
# sa = SensorsAnalytics(consumer, 'default', True)
# sa.register_super_properties({'$app_version' : '1.0.1', 'hahah' : 123})
# 
# def inFunction():
#     sa.track(1234, 'Test', {})
# 
# class XXX:
# 
#     def inClass(self):
#         sa.track(1234, 'Test', {})
# 
# p = {'$time' : int(time.time() * 1000), 'aaa' : 123}
# print(p)
# sa.track(1234, 'Test', p)
# print(p)
# sa.track(1234, 'Test', p)
# print(p)
# 
# inFunction()
# 
# XXX().inClass()
