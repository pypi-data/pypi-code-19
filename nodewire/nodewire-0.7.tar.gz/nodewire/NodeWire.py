'''
Copyright (c) 2016, nodewire.org
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by nodewire.org.
4. Neither the name of nodewire.org nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY nodewire.org ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL nodewire.org BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import time, threading
import requests
from nodewire.splitter import split, getsender, getnode
import asyncio
from nodewire.client import client
from configparser import ConfigParser

debug = False # False for deployment

class Message:
    def __init__(self, msg):
        words = split(msg)
        self.Address = words[0]
        self.Command = words[1] if len(words)>1 else words[0]
        self.Params = words[2:-1] if len(words)>2 else words[0]
        self.Sender = words[-1]

    def __str__(self):
        return self.Address + ' ' + self.Command + ' ' + ' '.join(p for p  in self.Params) + ' ' + self.Sender


class NodeWire:
    def __init__(self, cc, node_name='node', process=None):
        self.name = node_name
        self.address = self.name
        self.client = None
        self.terminated = False
        self.client = cc
        self.maintask = None
        self.called_connected =  False

        self.ack = False

        try:
            config = ConfigParser()
            config.read('nw.cfg')
            self.user = config['user']['account_name']
            self.pwd = config['user']['password']
            self.name = config['node']['name']
        except:
            print('error in configuration file')
            #quit()

        try:
            server = 'dashboard.nodewire.org'
            #server = 'localhost:5000'
            with requests.Session() as s:
                res = s.post('http://' + server + '/login', data={'email': self.user, 'pw': self.pwd})
                if res.ok:
                    r = s.get('http://' + server + '/config').json()
                    self.gateway = str(r['instance'])
                    self.address = self.gateway + ':' + self.name
                    self.server_address = r['server']
                    print(r['server'])
                else:
                    print('authentication failure')
                    quit()
        except Exception as ex:
            print('failed to connect to server')
            quit()

        if self.process_command:
            self.client.received = self.process_command


        self.process = process
        self.on_connected = None
        self.debug = False

    async def start(self, loop):
        await self.client.sendasync('cp Gateway user={} pwd={} {}\n'.format(self.user, self.pwd, self.gateway))

    def send(self, Node, Command, *Params):
        try:
            #todo rewrite this as format function
            cmd = Node + ' ' + Command + ' ' + ' '.join(param for param in Params) + (' ' + self.address if len(Params) != 0 else self.address)
            if self.debug:print(cmd)
            self.client.send(cmd+'\n')

        except Exception as ex:
            if self.debug:print('failed to send command over LAN')

    def waiter(self):
        if time.time()-self.last>5 and not self.called_connected:
            self.called_connected = True
            if self.on_connected:
                self.on_connected()
        else:
            threading.Timer(3, self.waiter).start()

    async def keepalive(self):
        await asyncio.sleep(60)
        while True:
            self.ack = False
            try:
                self.send('cp', 'keepalive')
            except:
                self.maintask.cancel()
                break
            await asyncio.sleep(5)
            if not self.ack:
                self.maintask.cancel()
                break
            await asyncio.sleep(300)

    def process_command(self, cmd):
        self.last = time.time()
        msg = Message(cmd)

        if self.debug: print(cmd)

        if msg.Command == 'ack':
            self.ack = True
            self.waiter()
        elif msg.Command == 'ping':
            self.send(msg.Sender, 'ThisIs')
        elif msg.Command == 'get' and msg.Params[0] == 'id':
            config = ConfigParser()
            config.read('nw.cfg')
            try:
                id = config['node']['id']
            except:
                id = 'None'
            self.send(msg.Sender, 'id', id)
        elif msg.Command == 'set' and msg.Params[0] == 'id':
            config = ConfigParser()
            config.read('nw.cfg')
            config['node']['id'] = msg.Params[1]
            with open('nw.cfg', 'w') as configfile:
                config.write(configfile)
        elif msg.Command == 'set' and msg.Params[0] == 'name':
            config = ConfigParser()
            config.read('nw.cfg')
            config['node']['name'] = msg.Params[1]
            self.name = msg.Params[1]
            self.address = self.gateway + ':' + self.name
            with open('nw.cfg', 'w') as configfile:
                config.write(configfile)
            self.send(msg.Sender, 'ThisIs')
        else:
            if self.process:
                self.process(msg)

    def run(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.client.connect(loop, serverHost=self.server_address)),
            loop.create_task(self.start(loop)),
            loop.create_task(self.keepalive())
        ]
        self.maintask = tasks[0]
        wait_tasks = asyncio.wait(tasks)
        try:
            loop.run_until_complete(wait_tasks)
        except KeyboardInterrupt:
            pass
        # loop.close()

if __name__ == '__main__':
    c = client()
    nw = NodeWire(c, 'pyNode')
    nw.debug = True
    nw.run()

