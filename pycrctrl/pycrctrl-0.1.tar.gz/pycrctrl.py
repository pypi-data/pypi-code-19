# -*- coding:utf-8 -*-

#Copyright (c) 2017, George Tokmaji

#Permission to use, copy, modify, and/or distribute this software for any
#purpose with or without fee is hereby granted, provided that the above
#copyright notice and this permission notice appear in all copies.
#
#THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys
import os

import subprocess
import queue
from _thread import start_new_thread
from time import sleep
from platform import architecture

import re
import configparser
from io import BytesIO
import logging

import urllib.request
try:
    import supybot.ircmsgs as ircmsgs
except ImportError:
    ircmsgs = None

import random

import tarfile
from enum import IntEnum

from gzip import GzipFile

#
# Helpers
#

class list(list):
    """ Extended list """
    
    def __lshift__(self, other):
        self.append(other)
        return self

    def __rshift__(self, other):
        if isinstance(other, list):
            item = self.__getitem__(len(self) - 1)
            try:
                other.append(item)
                self.pop()
            except Exception:
                raise TypeError("Cannot pass item to {}!".format(other)) from None
    
    # Methods
    
    def isEmpty(self):
        return len(self) == 0

class CmdResult(IntEnum):
    UnknownCommand = -1
    Success = 0
    SyntaxFail = 1
    RightsFail = 2
    RuntimeError = 3

class Updater(object):
    parent = None
    __current_revision = ""
    lookuptable = {"64bit" : "amd64", "32bit" : "i386"}
    
    def __init__(self, parent):
        self.parent = parent
        try:
            with open(os.path.join(self.parent.path, "snapshot.id"), "rb") as fobj:
                self.__current_revision = fobj.read().decode("utf-8")
        except OSError:
            pass
        
        start_new_thread(self.checkForUpdates, ())
    
    @property
    def current_revision(self):
        return self.__current_revision
    
    @current_revision.setter
    def current_revision(self, other):
        self.__current_revision = other
        if type(other) == str:
            try:
                other = other.encode("utf-8")
            except Exception:
                raise TypeError("Wrong datatype!") from None
        
        with open(os.path.join(self.parent.path, "snapshot.id"), "wb") as fobj:
            fobj.write(other)
    
    def checkForUpdates(self):
        while True:
            try:
                site = urllib.request.urlopen("http://openclonk.org/nightly-builds").read().decode("utf-8").split("<a href='/builds/nightly/snapshots/")
                site.remove(site[0])
                site = [i.split("' title")[0] for i in site]
                
                x = None
                for i in site:
                    x = re.match(r"openclonk-snapshot-(.*)-(.*)-{}-{}-.*".format(sys.platform, self.lookuptable[architecture()[0]]), i)
                    if x:
                        rev = x.group(2)
                        
                        if self.current_revision != rev:
                            self.current_revision = rev
                            self.loadNewSnapshot(i)
                        
                        break
                if not x:
                    self.parent.log.error("Updater.checkForUpdates: Regular expression doesn't match!")
            
            except Exception as e:
                self.parent.log.error(str(e.args[0]))
            finally:
                sleep(10)
    
    def loadNewSnapshot(self, f):
        self.parent.log.info("Downloading snapshot with id {}".format(self.current_revision))
        with open(os.path.join(self.parent.path, "snapshot"), "wb") as fobj:
            fobj.write(urllib.request.urlopen("http://openclonk.org/builds/nightly/snapshots/{}".format(f)))
        
        #extract the snapshot
        tar = tarfile.open(os.path.join(self.parent.path, "snapshot"), mode="r:bz2")
        tar.extractall(path=self.parent.path)
        self.parent.log.info("New snapshot has been extracted.")
        
        #get the openclonk-server autobuild
        site = json.loads(urllib.request.urlopen("https://autobuild.openclonk.org/api/v1/jobs").read().decode("utf-8"))
        
        for commit in site:
            for build in commit["builds"]:
                if re.match(r"{}-{}-.*".format(sys.platform, self.lookuptable[architecture()[0]]), build["platform"]["triplet"]):
                    for b in build["components"]:
                        reg = re.match(r".*/openclonk-server-(.*)-(.*)-(.*)-.*", str(b["path"])) #skip the engine check as the only useful one is openclonk-server
                        if reg and (reg.group(1), reg.group(2), reg.group(3)) == (self.current_revision[:-3], sys.platform, self.lookuptable[architecture()[0]]):
                            self.parent.log.info("Downloading autobuild with id {}".format(self.current_revision))
                            buffer = BytesIO()
                            buffer.write(urllib.request.urlopen("https://autobuild.openclonk.org/static/binaries/{}".format(b["path"])).read())
                            buffer.seek(0)
                            with open(os.path.join(self.parent.path, self.parent.config["Clonk"]["Engine"]), "wb") as fobj:
                                fobj.write(GzipFile(fileobj=buffer).read())
                                
                            self.parent.log.info("New openclonk-server build has been extracted.")
                            os.chmod(
                                os.path.join(self.parent.path, self.parent.config["Clonk"]["Engine"]), 
                                os.stat(os.path.join(self.parent.path, self.parent.config["Clonk"]["Engine"])).st_mode | 64)
                            return True

class PyCRCtrl(object):
    """Server control"""
    
    clonk = None
    thread_started = False
    stopped = False
    config = configparser.ConfigParser()
    
    scenario = ""
    commands = {}
    
    path = None
    config_path = None
    scenlist = []
    league_scenlist = []
    
    topic = "Kein laufendes Spiel."
    
    __state = "Lobby"
    __ingamechat = "aktiviert"
    
    updater = None
    log = None
    logfile = None
    shutdowned = False
    
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, text):
        if text in ["Lobby", "Lädt", "Läuft"]:
            self.__state = text
            self.setTopic("Aktuelles Szenario: {} | {}{} | Ingamechat ist {}.".format(self.scenario, self.state, (" | Liga" if self.scenario in self.league_scenlist else ""), self.ingamechat))
    
    @property
    def ingamechat(self):
        return self.__ingamechat
    
    @ingamechat.setter
    def ingamechat(self, text):
        if text in ["aktiviert", "deaktiviert"]:
            self.__ingamechat = text
            self.state = self.state
    
    def __init__(self, irc=None, path=".", config="pycrctrl.ini"):
        if ircmsgs is not None:
            self.irc = irc
        self.path = path
        self.loadConfigFile(config)
        self.setupLog()
        self.__ingamechat = "aktiviert" if self.config["Clonk"].getboolean("Autohost") else "deaktiviert" # important because there is no scenario hostet yet
        self.loadScenarioList()
        
        self.queue = queue.Queue(5)
        if self.config["Updater"].getboolean("Enabled"):
            self.updater = Updater(self)
    
    def loadScenarioList(self) -> None:
        if self.path == None:
            raise OSError("No path specified")
        
        with open(os.path.join(self.path,"scenarios.lst"), "r") as fobj:
            self.scenlist = [line.strip() for line in fobj.readlines()]
        
        with open(os.path.join(self.path, "scenarios_league.lst"), "r") as fobj:
            self.league_scenlist = [line.strip() for line in fobj.readlines()]
        
        self.log.debug("Scenario lists loaded.")
    
    def setupLog(self) -> None:
        if self.log:
            return
        
        self.log = logging.getLogger(type(self).__name__)
        self.log.setLevel(getattr(logging, self.config["Logging"]["Level"], logging.INFO))
        
        if not self.log.handlers:
            ch = logging.FileHandler(
                os.path.join(self.path, self.config["Logging"]["File"])
                )
            ch.setLevel(getattr(logging, self.config["Logging"]["Level"], logging.INFO))
            ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
            
            self.log.addHandler(ch)
            self.log.info("PyCRCtrl started.")
        
    def loadConfigFile(self, config) -> None:
        if self.path == None:
            raise OSError("No path specified")
        
        parser = configparser.ConfigParser()
        self.config_path = conf = os.path.join(self.path, config)
        
        if os.path.isdir(conf):
            raise OSError("{} is a directory!".format(conf))
        
        elif os.path.isfile(conf):
            self.config.read(conf)
        
        elif not os.path.exists(conf):
            c = """[General]
UseLogfile=true
Prefix=@

[Clonk]
Engine=clonk
Encoding=utf-8
Commandline=/fullscreen /lobby:300 /config:config.txt /record /faircrew
Autohost=false

[IRC]
Ingamechat=true
    
    [Channels]
    Parent="#clonk-SGGP"
    Ingame="#clonk-SGGP-ingame"

[Updater]
Enabled=false

[RegExps]
LobbyStart=((?:Los geht's!|Action go!)\\s*)
Start=Start!
PlayerJoin=^Client (.+) (?:verbunden|connected)\.\s*$
PlayerLeave=^Client (.+) (?:entfernt|removed).*
Shutdown=Spiel ausgewertet.*
Autobuild=.*/openclonk-server-(.*)-(.*)-(.*)-.*
Snapshot=openclonk-snapshot-(.*)-(.*)-{}-{}-."""
            
            self.config.read_string(c)
            with open(conf, "w") as fobj:
                self.config.write(fobj)
    
    def startClonk(self):
        try:
            while True:
                if self.scenario == "":
                    if self.queue.empty() == False:
                        self.scenario = self.queue.get()
                    else:
                        self.scenario = random.choice(self.scenlist).splitlines()[0]
                
                self.clonk = subprocess.Popen(
                    './{} {} "{}"'.format(self.config["Clonk"]["Engine"], self.config["Clonk"]["Commandline"] + " " + self.config["Clonk"]["commandlinePrefix"]  + ("league" if self.scenario in self.league_scenlist else "noleague"), self.scenario),
                    0,
                    None,
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.STDOUT,
                    shell=True,
                    cwd=self.path,
                    encoding=self.config["Clonk"]["Encoding"]
                    )
                self.state = "Lobby"
                self.log.info("Scenario: {}".format(self.scenario))
                self.readServerOutput()
                if self.config["Clonk"].getboolean("Autohost") == False:
                    self.thread_started = False
                    self.setTopic("Kein laufendes Spiel.") 
                    break
        
        finally:
            if self.clonk:
                self.clonk.stdin.close()
        
        return (CmdResult.Success, "")
    
    def readServerOutput(self):
        while True:
            try:
                output = self.clonk.stdout.readline()
                if re.match(self.config["RegExps"]["Shutdown"], output):
                    self.clonk.stdin.close()
                elif output == "" and self.clonk.poll() is not None:
                    if self.clonk:
                        self.log.debug("poll() is not None, shutting down")
                        self.clonk.stdin.close()
                        self.clonk = None
                        self.scenario = ""
                        return
                
                elif output:
                    output = output.splitlines()[0]
                    #output = output.decode("utf-8").splitlines()[0]
                    output = output[(output.find("] ") if output.find("] ") != -1 else -2)+len("] "):]
                    
                    if output[0] == ">":
                        output = output[1:]
                    
                    self.log.info(output)
                    part = self.isMessage(output)
                    if part and part.group(0) != self.irc.nick:
                        #self.log.info(output)
                        cmd = part.group(3).split(" ", 1)
                        found = False
                        x = None
                        try:
                            if len(cmd) > 0:
                                key = cmd[0].splitlines()[0]
                                if not hasattr(self, key):
                                    raise RuntimeError
                                try:
                                    x = getattr(self, key)(cmd[1].split(" "), user=part.group(1))
                                except IndexError:
                                    x = getattr(self, key)(user=part.group(1))
                                    break
                        
                        except RuntimeError:
                            self.writeToServer('Unbekannter Befehl: "' + part.group(2) + '"!')
                        if x:
                            if type(x) == tuple and x[1] != "":
                                self.writeToServer(x[1])
                            del x
                    
                    if re.match(self.config["RegExps"]["LobbyStart"], output):
                        self.state = "Lädt"
                
                    elif re.match(self.config["RegExps"]["Start"], output):
                        self.state = "Läuft"
                
                    if self.irc and self.ingamechat == "aktiviert":
                        if output.find("<" + self.irc.nick + ">") == -1:
                            if self.isMessage(output) and "[IRC]" not in output and self.config["General"]["Prefix"] not in output:
                                self.irc.reply("[Clonk]{}".format(output), to=self.config["Channels"]["Ingame"])
                        
                            elif any((re.match(self.config["RegExps"]["PlayerJoin"], output), re.match(self.config["RegExps"]["PlayerLeave"], output))):
                                self.irc.reply(output, to=self.config["Channels"]["Ingame"])
                
                
            except KeyboardInterrupt:
                if self.clonk.stdin:
                    self.clonk.stdin.close()
            
            except Exception as e:
                self.log.exception(e.args[0])
                continue
        
        return (CmdResult.Success, "")
    
    def doPrivmsg(self, msg):
        if not (self.irc and self.ingamechat == "aktiviert"):
            return
        for channel in msg.args[0].split(","):
            if channel == self.config["Channels"]["Ingame"] and msg.nick != self.irc.nick:
                self.writeToServer("[IRC]<{}> {}".format(msg.nick, msg.args[1]))
    
    #
    # Commands
    #
    
    def host(self, scenario=None, user=None) -> str:
        if not scenario:
            return (CmdResult.SyntaxFail, "Bitte gib einen Szenarionamen an!")
        if hasattr(scenario, "decode"):
            try:
                scenario = scenario.decode(self.config["Clonk"]["Encoding"])
            except:
                self.log.warning("Unable to decode {}".format(scenario))
                return (CmdResult.RuntimeError, "Dekodierfehler. Bitte kontaktiere den Hoster dieses Servers.")
        
        scenario = scenario.splitlines()[0]
        if scenario == "random":
            scenario = random.choice(self.scenlist).splitlines()[0]
        
        elif scenario not in self.scenlist:
            return (CmdResult.SyntaxFail,'Szenario "{}" wurde nicht gefunden!'.format(scenario))
        
        if self.thread_started == False:
            self.scenario = scenario
            self.thread_started = True
            start_new_thread(self.startClonk,())
            return (CmdResult.Success, 'Szenario "{}" wird jetzt gehostet.'.format(scenario))
        
        if not self.queue.full():
            self.queue.put(scenario)
            return (CmdResult.Success, 'Szenario "{}" wurde der Warteschlange hinzugefügt.'.format(scenario))
        else:
            return (CmdResult.RuntimeError, "Die Warteschlange ist voll!")
    
    def start(self, time=None, user=""):
        """Startet das Spiel."""
        self.stopped = False
        if time:
            try:
                time = int(time[0])
            except:
                time = 5
            self.writeToServer("/start {}".format(time))
        else:
            self.writeToServer("/start")
        
        return (CmdResult.Success, "")
    
    
    def stop(self, prm=None, user=""):
        """Stoppt den Countdown."""
        def stopping(self):
            while self.clonk and self.stopped:
                self.writeToServer("/start 60000")
                if self.stopped == False:
                    return
                sleep(100)
        
        if self.stopped == False:
            self.stopped = True
            start_new_thread(stopping, (self,))
        
        return (CmdResult.Success, "")
    
    
    def help(self, prm=None, user=""):
        """Gibt die Hilfe aus."""
        self.writeToServer("Verfügbare Befehle:")
        for text, function in self.commands.items():
            self.writeToServer("{} -- {}".format(text, function.__doc__))
        
        return (CmdResult.Success, "")
    
    
    def displayQueue(self, prm=None, user=""):
        """Gibt die Warteschlange aus."""
        self.writeToServer("Warteschlange:")
        
        for i,scen in enumerate(self.queue.queue):
            self.writeToServer("{}. {}".format(i+1, scen))
        
        return (CmdResult.Success, "")
    
    
    def list(self, prm=None, user=""):
        """Zeigt die Szenarioliste an."""
        self.writeToServer("Szenarienlist:\n-------------")
        for scen in self.scenlist:
            self.writeToServer(scen + ("(Liga)" if scen in self.league_scenlist else ""))
        
        return (CmdResult.Success, "")
    
    def ircCommands(self, prm=None, user=""):
        """Enthält Befehle zur Steuerung der IRC-Funktionen."""
        if not prm:
            return (CmdResult.SyntaxFail, "")
        
        if prm[0] == "ingamechat":
            if prm[1] == "off":
                self.ingamechat = "deaktiviert"
            elif prm[1] == "on":
                self.ingamechat = "aktiviert"
        
        return (CmdResult.Success, "")
    
    #
    # Methods
    #
    
    def isMessage(self, msg):
        return re.match(self.config["RegExps"]["Message"].format(prefix=self.config["General"]["Prefix"]), msg)
    
    def getMessageNick(self, msg):
        m = self.isMessage(msg)
        if m:
            return m.group(1)
    
    def addCommand(self, function, text):
        self.commands[text.split(" ")[0]] = function
        return self
    
    def addScenario(self, link):
        name = ""
        for item in link.split("/"):
            if re.match(r"(.*)\.[oc][c4]s",item):
                name = item
                break
        
        site = urllib.request.urlopen(link).read() #WARNING: Raises an error if the link is invalid!
        with open(os.path.join(self.path, name),"wb") as fobj:
            fobj.write(site)
        
        try:
            self.scenlist.index(name)
        except Exception:
            self.scenlist.append(name)
        return self
    
    def writeToServer(self, text=None) -> tuple:
        if text == None and self.clonk == None:
            return (CmdResult.RuntimeError, "")
        elif type(text) != str:
            try:
                text = text.decode(self.config["Clonk"]["Encoding"])
            except:
                raise IOError("Cannot write anything else to the server except the following data types: bytes, str (got {})".format(type(text).__name__))
        
        if self.clonk and self.clonk.stdin:
            self.clonk.stdin.write(text + "\n")
            self.clonk.stdin.flush()
        return (CmdResult.Success, "")
    
    def setTopic(self, text=None) -> None:
        if not self.irc:
            return
        
        if type(text) != str:
            try:
                text = text.decode(self.config["Clonk"]["Encoding"])
            except:
                raise TypeError("bytes or str expected, got {}".format(type(text).__name__))
        
        if self.topic != text:
            self.topic = text
            channel = self.config["Channels"]["Ingame"]
            if not channel.startswith("#"):
                raise ValueError("Invalid channel: {} (ident: {})".format(channel, channel == "#clonk-SGGP-ingame"))
            self.irc.sendMsg(ircmsgs.topic(self.config["Channels"]["Ingame"], text))
    
    def shutdown(self):
        if self.shutdowned:
            return
        
        self.log.info("Shutting down...")
        
        del self.updater
        
        if self.clonk and self.clonk.stdin and not self.clonk.stdin.closed:
            self.clonk.stdin.close()
        
        with open(self.config_path, "w") as fobj:
            self.config.write(fobj)
            self.log.debug("Config file saved.")
        
        with open(os.path.join(self.path, "scenarios.lst"), "w") as fobj:
            fobj.writelines(self.scenlist)
        
        with open(os.path.join(self.path, "scenarios_league.lst"), "w") as fobj:
            fobj.writelines(self.league_scenlist)
        
        self.log.debug("Scenario lists saved.")
        self.setTopic("Kein laufendes Spiel.")
        logging.shutdown()
        self.shutdowned = True
