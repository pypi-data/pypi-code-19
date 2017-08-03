#-------------------------------------------------------------------------------
#Targeting:     Python 2 and 3
#Use:           Wrapper to implement a socketIO connection to a MF controller
#-------------------------------------------------------------------------------

from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from threading import Thread

#-------------------------------------------------------------------------------

class MF_socketIO:

    def __init__(self, controllerBaseUrl, controllerPort, password):
        self.baseUrl = controllerBaseUrl
        self.port = controllerPort
        self.password = password

        #create a new socketIO client connection to the controller
        self.socket = SocketIO(self.baseUrl, self.port, LoggingNamespace)

        #hub currently expects imediate auth after connecting
        self.auth(password)

        #setup thread for reciving events - not used yet
        self.receive_events_thread = Thread(target=self.on_message_recived)
        self.receive_events_thread.daemon = True
        self.receive_events_thread.start()

    def auth(self, password):

        def on_auth_result(*args):
            #todo: process the result here or pass to callback
            #print args
            pass

        self.socket.emit('auth', {'password': self.password}, on_auth_result)
        self.socket.wait_for_callbacks(seconds=10)

    def on_message_recived(self):
        self.socket.wait()
        #todo: add processing of incoming messages
        #no requirement for this yet

    def get(self, command, callback):
        self.socket.emit(command, callback)
        self.socket.wait_for_callbacks(seconds=5)

    def getWithParam(self, command, param, callback):
        self.socket.emit(command, param, callback)
        self.socket.wait_for_callbacks(seconds=5)

    def send(self, room, command, score):
        self.socket.emit('sendCommand', room, command, score)

#-------------------------------------------------------------------------------
