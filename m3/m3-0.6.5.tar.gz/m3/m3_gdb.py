#
#
# Andrew Lukefahr
# lukefahr@umich.edu
#
#

import os
import socket
import sys

import binascii

class GdbRemote:
    
    def debug( this, s):
        print ('DEBUG: ' + str(s) )

    def __init__(this, tcp_port = 10001):
        assert( type(tcp_port) == int) 
        
        #open our tcp/ip socket
        this.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)

        #Bind socket to local host and port
        try:
            this.sock.bind( ('localhost', tcp_port) )
        except socket.error as msg:
            this.debug('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] )
            raise Exception()

        this.debug( 'Listening on port: ' + str(tcp_port))
        this.sock.listen(1) #not sure why 1
        
        
    def _run(this):
        
        while True:
            [conn, client] = this.sock.accept()
            this.debug('New connection from: ' + str(client))
            
            #grab the opening '+'
            this.debug('Grabbing opening +')
            plus = conn.recv(1)
            assert(plus == '+')

            while True:
                newdata = conn.recv(256)
                
                if not newdata:
                    break #disconnect

                this.debug('Incomming data: ' + str(newdata) ) 
                msg  = this._parse_message( newdata)
                
                if msg: 
                    this.debug('Message: ' + str(msg) )

            this.debug('Closing connection with: ' + str(client))
            conn.close()

    def _parse_message(this, newdata):
        # static buffer to tack on the new data
        # (plus fun way to make a static-ish function variable)
        try: this.data += newdata
        except AttributeError: this.data = newdata
        
        msg = None
        chkIdx = this.data.find('#')
        
        # look for a checksum marker + 2 checksum bytes
        if (chkIdx > 0) and (len(this.data) >= chkIdx + 3):
            this.debug ('Found # at: ' + str(chkIdx) )

            msg = this.data[:chkIdx+4]
            this.data = this.data[chkIdx+4:]
           
            chksum = 0
            for byte in msg[0:chkIdx]:
                chksum += ord(byte)
            this.debug('Checksum cacl:' + str(chksum) + ' sent:' + msg[chkIdx+1:])


            this.debug('Parsed raw message : ' + str(msg) ) 
            this.debug('Advanced raw data: ' + str(this.data) ) 

        return msg

                     

         

 


if __name__ == '__main__':
   
   gdb = GdbRemote()

   gdb._run()
