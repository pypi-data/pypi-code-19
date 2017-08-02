from fluent import sender
from fluent import event
import datetime

sender.setup('fluentd.test', host='localhost', port=24224)



class Logger:
    def __init__(self,host,port,name):
        self.host = host
        self.port = port
        self.name = name
        sender.setup('fluentd.justpith', host=self.host, port=self.port)

    def log(self,message,source):
        time  = datetime.datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')
        output = {
            "time": time,
            "output": message,
            "source": source
        }
        event.Event(self.name, output)