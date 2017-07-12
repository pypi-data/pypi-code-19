import json
from mns.account import Account
from mns.queue import *
from .utils import import_attribute

class Worker(object):
    def __init__(self, name):
        from .settings import QUEUES
        queue = QUEUES[name]
        if queue['QUEUE_TYPE'] == 'mns':
            print queue['QUEUE_CONNECTION']['ENDPOINT'], queue['QUEUE_CONNECTION']['ACCID'],
            queue['QUEUE_CONNECTION']['ACCKEY']
            connection = Account(
                queue['QUEUE_CONNECTION']['ENDPOINT'],
                queue['QUEUE_CONNECTION']['ACCID'],
                queue['QUEUE_CONNECTION']['ACCKEY'])

            self.queue = connection.get_queue(name)
            print 'aliyun mns connection ok'
            self.queue_consumer_func = import_attribute(queue['QUEUE_CONSUMER_MODULE'])

    def run(self):
        while True:
            try:
                try:
                    recv_msg = self.queue.receive_message(1)
                    msg_dict_handle = json.loads(recv_msg.message_body)
                    print msg_dict_handle

                    try:
                        self.queue_consumer_func(*msg_dict_handle.get('args', []), **msg_dict_handle.get('kwargs', {}))
                    except Exception as e:
                        print str(e), 'filterrerer'
                        raise e

                    try:
                        self.queue.delete_message(recv_msg.receipt_handle)
                        # logging.info("Delete Message Succeed!  ReceiptHandle:%s" % recv_msg.receipt_handle)
                    except Exception, e:
                        raise e
                        # pass
                        # logging.info("Delete Message Fail! Exception:%s\n" % e)
                except MNSExceptionBase, e:
                    print str(e), 'xxxxxxxxx'
                    if e.type == "QueueNotExist":
                        pass
                        # logging.info("Queue not exist, please create queue before receive message.")
                        # sys.exit(0)
                    elif e.type == "MessageNotExist":
                        pass
                        # logging.info("Queue is empty!")
                        # sys.exit(0)
                        # logging.info("Receive Message Fail! Exception:%s\n" % e)
                    else:
                        print e
                        raise e
            except Exception, e:
                print str(e), 'billllerrorroro'