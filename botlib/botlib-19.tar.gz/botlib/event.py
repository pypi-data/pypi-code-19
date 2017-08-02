# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" event handling classes. """

from .utils import days, tname, to_time
from .object import Default, Object, slice
from .register import Register
from .trace import get_exception

import logging

class Parsed(Default):

    """ parsed contains all the arguments that are _parsed from an event. """

    default = ""

    def __getattr__(self, name):
        if name == "args":
            self.args = []
        if name == "cmnd":
            self.cmnd = ""
        if name == "fields":
            self.fields = []
        if name == "index":
            self.index = None
        if name == "ignore":
            self.ignore = Register()
        if name == "notwant":
            self.notwant = Object()
        if name == "rest":
            self.rest = ""
        if name == "switch":
            self.switch = Object()
        if name == "uniq":
            self.uniq = []
        if name == "want":
            self.want = Object()
        if name == "words":
            self.words = []
        return super().__getattr__(name)

    def clear(self):
        self.args = []
        self.cmnd = ""
        self.fields = []
        self.index = None
        self.ignore = Register()
        self.notwant = Object()
        self.rest = ""
        self.switch = Object()
        self.want = Object()
        self.words = []
        self.uniq = []

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
            except (IndexError, ValueError):
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
                self.rest += value + " "
                continue
            if key == "index":
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
                if last == "-":
                    continue
                if counter > 1:
                    self.fields.append(key)
                self.args.append(key)
                self.rest += key + " "
            else:
                if counter > 1:
                    self.fields.append(value)
                self.args.append(value)
                self.rest += str(value) + " "
        self.rest = self.rest.strip()
        return self

class Event(Default):

    """ Events are constructed by bots based on the data they receive. This class provides all functionality to handle this data (parse, dispatch, show). """

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
        """ dispatch the object to the functions registered in the _funcs member. """
        for func in self._funcs:
            logging.info("! event %s (%s)" % (self._parsed.txt, self.origin))
            try:
                func(self)
            except:
                logging.error(get_exception())

    def display(self, obj=None, keys=[], txt="", direct=""):
        """ display the content of an object. """
        res = ""
        if not obj:
            obj = self
        if not keys:
            keys = obj.keys()
        for key in keys:
            val = getattr(obj, key, None)
            if val:
                res += str(val).strip() + " "
        d = days(obj)
        res += " - %s" % d
        if txt:
            res = "%s %s" % (txt.strip(), res.strip())
        res = res.strip()
        if direct:
            self.direct(res)
        else:
            self.reply(res)

    def id(self):
        """ return a bot type + server host as a event id. """
        return self.btype + "." + self.server

    def join(self, *args, **kwargs):
        """ join threads started while handling this event. """
        for thr in self._thrs:
            thr.join(*args, **kwargs)

    def ok(self, txt=""):
        """ reply with 'ok'. """
        self.reply("ok %s" % txt)

    def parse(self, txt=""):
        """ convenience method for the _parsed.parse() function. resets the already available _parsed. """
        txt = txt or self.txt
        if not self._result:
            self._result = []
        self._parsed.clear()
        self._parsed.parse(txt)

    def prep(self):
        """ parse and store the matching functions in the _funcs attribute. """
        from .space import kernel
        self._funcs = kernel.get_handlers(self._parsed.cmnd)
        return self._funcs

    def prompt(self):
        """ give a prompt on the corresponding cli bot. """
        from .space import fleet
        if self.btype != "cli":
            return
        bots = fleet.get_type("cli")
        for bot in bots:
            bot.prompt()

    def say_id(self, id, channel, txt):
        """ say something to id on fleet bot. """
        from .space import fleet
        fleet.say_id(id, channel, txt)

    def reply(self, txt):
        """ give a reply to the origin of this event. """
        self.add(txt)

    def show(self):
        """ show the event on the server is originated on. """
        for txt in self._result:
            self.direct(txt)

