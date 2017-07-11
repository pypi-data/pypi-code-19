# botlib/event.py
#
# Copyright 2016,2017 Bart Thate
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# * As the creator of this piece of software, Bart Thate, i disclaim all rights on the code contained in this software package.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

""" event handling classes. """

from .utils import days, locked, stripped, tname, to_time
from .error import ENOFUNC
from .object import Default, Object, slice
from .register import Register
from .trace import get_exception

import logging

class Parsed(Default):

    """ parsed contains all the arguments that are _parsed from an event. """

    default = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name == "cmnd":
            self.cmnd = ""
        if name == "switch":
            self.switch = Object()
        if name == "want":
            self.want = Object()
        if name == "ignore":
            self.ignore = Register()
        if name == "notwant":
            self.notwant = Object()
        if name == "args":
            self.args = []
        if name == "rest":
            self.rest = ""
        if name == "fields":
            self.fields = []
        if name == "words":
            self.words = []
        if name == "index":
            self.index = None
        return super().__getattr__(name)

    def clear(self):
        self.cmnd = ""
        self.switch = Object()
        self.want = Object()
        self.ignore = Register()
        self.notwant = Object()
        self.args = []
        self.rest = ""
        self.fields = []
        self.words = []
        self.index = None
        
    def parse(self, txt):
        """ parse txt to determine cmnd, args, rest and other values. adds a _parsed object to the event. """
        from .space import kernel
        txt = str(txt)
        if txt.endswith("&"):
            self.threaded = True
            txt = self.txt[:-1]
        splitted = txt.split()
        quoted = False
        key2 = ""
        counter = -1
        for word in splitted:
            counter += 1
            if counter == 0:
                if self.command:
                    self.cmnd = self.command
                    continue
                if self.cc and self.cc != word[0]:
                    continue                
                if self.cc:
                    word = word[1:]
                if word:
                    self.cmnd = word.lower().strip()
                continue
            try:
                key, value = word.split("=", 1) 
            except (IndexError,ValueError):
                key = ""
                value = word 
            if "http" in key:
                key = ""
                value = word
            if value.startswith('"'):
                if value.endswith('"'):
                    value = value[1:-1]
                    self.words.append(value)
                else:
                    key2 = key
                    value = value[1:]
                    self.words.append(value)
                    quoted = True
                    continue
            if quoted:
                if '"' in value:
                    value, *restant = value.split('"')
                    key = key2
                    self.words.append(value)
                    value = " ".join(self.words)
                    value += "".join(restant)
                    self.words = []
                    quoted = False
                else:
                    self.words.append(value)
                    continue
            if quoted:
                self.words.append(value)
                continue
            if "http" in value:
                self.args.append(value)
                self.rest += " " + value
                continue
            if key=="index":
                self.index = int(value)
                continue
            if key == "start":
                self.start = to_time(value)
                continue 
            if key == "end":
                self.end = to_time(value)
                continue 
            if key == "uniq":
                if not self.uniq:
                     self.uniq = []
                self.uniq.append(value)
            if value.startswith("+") or value.startswith("-"):
                try:
                    val = int(value)
                    self.time_diff = val
                    if val >= -10 and val <= 10:
                        self.karma = val
                except ValueError:
                    self.time_diff = 0
            if key and value:
                pre = key[0]
                op = key[-1]
                post = value[0]
                last = value[-1]
                if key.startswith("!"):
                     key = key[1:]
                     self.switch[key] = value
                     continue
                if post == "-":
                     value = value[1:]
                     self.ignore.register(key, value)
                     continue
                if op == "-":
                     key = key[:-1]
                     self.notwant[key] = value
                     continue
                if last == "-":
                    value = value[:-1]
                self.want[key] = value 
                if last == "-" :
                    continue
                if counter > 1:
                    self.fields.append(key)
                self.args.append(key)
                self.rest += " " + key
            else:
                if counter > 1:
                    self.fields.append(value)
                self.args.append(value)
                self.rest += " " + str(value)
        self.rest = self.rest.lstrip()
        return self

class Event(Default):

    default = ""

    def __getattr__(self, name):
        if name == "channel":
            self["channel"] = "#botlib"
        if name == "_parsed":
            self._parsed = Parsed(slice(self, ["cc", "txt"]))
        if name == "_result":
            self._result = []
        val = super().__getattr__(name)
        return val

    def add(self, txt):
        """ say something on a channel, using the bot available in the fleet. """
        self._result.append(txt)

    def announce(self, txt):
        """ announce on all fleet bot. """
        from .space import kernel
        kernel.announce(txt)

    def direct(self, txt):
        """ output txt directly. """
        from .space import fleet
        if "_socket" in self:
            try:
                self._socket.write(txt)
            except TypeError:
                self._socket.write(str(txt))
            self._socket.write("\n")
            self._socket.flush()
        else:
            fleet.say_id(self.id(), self.channel, txt)

    def dispatch(self):
        """ dispatch based on the provided event. """
        for func in self._funcs:
            try:
                func(self)
            except Exception as ex:
                logging.error(get_exception())
        return self

    def display(self, object=None, keys=[], txt="", direct=""):
        """ display the content of an objectect. """
        res = ""
        if not object:
            object = self
        if not keys:
            keys = object.keys()
        for key in keys:
            val = getattr(object, key, None)
            if val:
                res += " " + str(val).strip()
        d = days(object)
        res += " - %s" % d
        if txt:
            res = "%s %s" % (txt, res.strip())
        if direct:
            self.direct(res.strip())
        else:
            self.reply(res.strip())

    def handle(self):
        """ handle an event. """
        from .space import kernel
        self.parse()
        self._funcs = kernel.get_funcs(self._parsed.cmnd)
        self._state.running = self._parsed.cmnd
        try:
            self.dispatch()
        except:
            logging.error(get_exception())
            return self
        self.show()
        return self

    def id(self):
        return self.btype + "." + self.server

    def join(self, *args, **kwargs):
        """ join threads started while handling this event. """
        for thr in self._thrs:
            thr.join(*args, **kwargs)

    def ok(self, txt=""):
        """ reply with 'ok'. """
        self.reply("ok %s" % txt)

    def parse(self, txt=""):
        txt = txt or self.txt
        if not self._result:
            self._result = []
        self._parsed.clear()
        self._parsed.parse(txt)

    def say_id(self, id, channel, txt):
        """ say something to id on fleet bot. """
        from .space import fleet
        fleet.say_id(id, channel, txt)
   
    def reply(self, txt):
        """ give a reply to the origin of this event. """
        if type(txt) in [list, tuple]:
            txt = ",".join([str(x) for x in txt])
        self.add(txt)

    def show(self):
        """ show the event on the server is originated on. """
        for txt in self._result:
            self.direct(txt)
        self._done = True
        self.ready()

    def wait(self, sec=None):
        """ wait for event to finish. """
        super().wait()
        for thr in self._thrs:
            logging.warn("# join %s" % tname(thr))
            thr.join(sec)
