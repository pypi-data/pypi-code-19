#!/usr/bin/env python3

import json
import re
import ssl
import threading
import time
import websocket


class HackChat:
    """This class receives and sends data from and to hack.chat.

    Return values:
        Data received by the callback function without explicit access
        of functions in this class will be one of the following
        (<dict>):
        {
            "type": "message",
            "nick": <str>; the senders' nickname,
            "text": <str>; the senders' message,
            "trip": <str>; the senders' tripcode if the sender has one
        }
        {
            "type": "online add",
            "nick": <str>; nickname of user who just joint the channel
        }
        {
            "type": "online remove",
            "nick": <str>; nickname of user who just left the channel
        }
        {
            "type": "invite",
            "nick": <str>; the nickname of user who invited you to a
                    channel (might be your own if you invited someone
                    else),
            "channel": <str>; name of the channel invited to
        }
        {
            "type": "banned",
            "nick": <str>; the nickname of the banned user
        }
        {
            "type": "unbanned",
            "ip": <str>; the IP address of the unbanned user
        }
        {
            "type": "broadcast",
            "text": <str>; the message broadcasted to hack.chat
        }
        {
            "type": "warn",
            "warning": <str>; an explanation of why you have been
                       warned
        }
        {
            "type": "error",
            "error": <str>; the websocket error
        }

        Possible warnings (<str>):
            "Nickname must consist of up to 24 letters, numbers, and "
            + "underscores"
            "Cannot impersonate the admin"
            "Nickname taken"
            "Your IP is being rate-limited or blocked."
            "You are joining channels too fast. Wait a moment and try "
            + "again."

    Example:
        #!/usr/bin/env python3

        import hclib


        # Make a callback function with two parameters.
        def on_message(connector, data):
            # The second parameter (<data>) is the data received.
            print(data)
            print(connector.onlineUsers)
            # Checks if someone joined the channel.
            if data["type"] == "online add":
                # Sends a greeting the person joining the channel.
                connector.send("Hello {}".format(data["nick"]))


        if __name__ == "__main__":
            hclib.HackChat(on_message, "myBot", "botDev")
    """

    def __init__(self, callback, nick, channel, pwd=None,
                 url="wss://hack.chat/chat-ws", require_cert=True):
        """Initializes values.

        Keyword arguments:
            callback -- <function>; name of function to receive data
            nick -- <str>; nickname to use upon connecting
            channel -- <str>; the channel to connect to
            pwd -- <str>; password that generates a tripcode upon
                   entering
            url -- <str>; the hack.chat instance
            require_cert -- <bool>; set to <True> to prevent connecting
                            if the websites' certificate is invalid
        """
        self._callback = callback
        self._nick = nick
        self._channel = channel
        self._pwd = pwd
        self._url = url
        self._onlineUsers = []
        self._ws = websocket.WebSocketApp(self._url,
                                          on_message=self._on_message,
                                          on_error=self._on_error)
        self._ws.on_open = self._on_open
        opt = None if require_cert else {"cert_reqs": ssl.CERT_NONE}
        self._ws.run_forever(sslopt=opt)

    @property
    def nick(self):
        """The nickname being used on <channel>."""
        return self._nick

    @property
    def channel(self):
        """The hack.chat channel connected to."""
        return self._channel

    @property
    def pwd(self):
        """The password used."""
        return self._pwd

    @property
    def url(self):
        """The hack.chat instance connected to."""
        return self._url

    @property
    def onlineUsers(self):
        """"A <list> of nicknames (<str>) of users online."""
        return self._onlineUsers

    def _on_open(self, ws):
        """Joins the hack.chat channel and starts pinging."""
        nick = self._nick
        if self._pwd:
            nick += "#{}".format(self._pwd)
        data = {"cmd": "join", "channel": self._channel, "nick": nick}
        self._send_packet(data)
        self._thread = True
        threading.Thread(target=self._ping).start()

    def _on_error(self, err):
        """Handles websocket errors."""
        self._callback(self, {"type": "error", "error": err})

    def _ping(self):
        """Pings periodically to retain the websocket connection."""
        while True:
            time.sleep(60)
            if self._thread:
                self._send_packet({"cmd": "ping"})

    def _on_message(self, ws, msg):
        """Sends and receives data to the callback function."""
        result = json.loads(msg)
        if result["cmd"] == "chat":
            data = {"type": "message", "nick": result["nick"],
                    "text": result["text"]}
            if "trip" in result:
                data["trip"] = result["trip"]
            self._callback(self, data)
        elif result["cmd"] == "onlineSet":
            self._onlineUsers += result["nicks"]
        elif result["cmd"] == "onlineAdd":
            self._onlineUsers.append(result["nick"])
            self._callback(self, {"type": "online add",
                                 "nick": result["nick"]})
        elif result["cmd"] == "onlineRemove":
            self._onlineUsers.remove(result["nick"])
            self._callback(self, {"type": "online remove",
                                 "nick": result["nick"]})
        elif result["cmd"] == "info" and " invited " in result["text"]:
            if "You invited " in result["text"]:
                name = self._nick
            else:
                space = re.search(r"\s", result["text"])
                name = result["text"][:space.start()]
            link = re.search("\?", result["text"])
            channel = result["text"][link.end():]
            self._callback(self, {"type": "invite", "nick": name,
                                 "channel": channel})
        elif result["cmd"] == "info" and " IPs " in result["text"]:
            data = result["text"].split()
            self._callback(self, {"type": "stats", "IPs": data[0],
                                 "channels": data[4]})
        elif result["cmd"] == "info" and "Banned " in result["text"]:
            nick = result["text"][len("Banned "):]
            self._callback(self, {"type": "banned", "nick": nick})
        elif result["cmd"] == "info" and "Unbanned " in result["text"]:
            ip = result["text"][len("Unbanned "):]
            self._callback(self, {"type": "unbanned", "ip": ip})
        elif (result["cmd"] == "info"
              and "Server broadcast: " in result["text"]):
            txt = result["text"][len("Server broadcast: "):]
            self._callback(self, {"type": "broadcast", "text": txt})
        elif result["cmd"] == "info":
            self._callback(self, {"type": "list users",
                                 "text": result["text"]})
        elif result["cmd"] == "warn":
            data = {"type": "warn", "warning": result["text"]}
            if "Could not find " in result["text"]:
                data["warning"] = "user to ban not found"
                data["nick"] = result["text"][len("Could not find "):]
            self._callback(self, data)

    def _send_packet(self, data):
        """Sends <data> (<dict>) to hack.chat."""
        self._ws.send(json.dumps(data))

    def send(self, msg):
        """Send <msg> (<str>) to the channel that last sent data.

        The following data may be sent to the callback function.
            {
                "type": "warn",
                "warning": "You are sending too much text. Wait a "
                           + "moment and try again.\nPress the up "
                           + "arrow key to restore your last message."
            }
        """
        self._send_packet({"cmd": "chat", "text": msg})

    def invite(self, nick):
        """Invites <nick> (<str>) to a randomly generated channel.

        This invite will only be visible to <nick>. The callback
        function will receive the data such as the channel.
        A warning having one of the following formats might be sent to
        the callback function.
            {
                "type": "warn",
                "warning": "You are sending invites too fast. Wait a "
                           + "moment before trying again."
            }
            {
                "type": "warn",
                "warning": "Could not find user in channel"
            }
        """
        self._send_packet({"cmd": "invite", "nick": nick})

    def stats(self):
        """Sends hack.chat statistics to the callback function.

        The following data will be sent to the callback function.
            {
                "type": "stats",
                "IPs": <str>; number of unique IPs connected to
                       hack.chat,
                "channels": <str>; number of channels on hack.chat
            }
        """
        self._send_packet({"cmd": "stats"})

    def ban(self, nick):
        """Bans <nick> (<str>) from hack.chat for 24 hours.

        <pwd> must be that of a moderators' or admins' to use this.
        You cannot ban a moderator or admin.
        The callback function will receive one of the following.
            {
                "type": "warn",
                "warning": "user to ban not found",
                "nick": <str>; nickname of user to ban that wasn't found
            }
            {
                "type": "warn",
                "warning": "Cannot ban moderator"
            }
        """
        self._send_packet({"cmd": "ban", "nick": nick})

    def unban(self, ip):
        """Unbans the IP <ip> (<str>)

        <pwd> must be that of a moderators' or admins' to use this.

        The callback function will receive the following data.
            {
                "type": "unbanned"
                "ip": <str>; IP of unbanned user
            }
        """
        self._send_packet({"cmd": "unban", "nick": nick})

    def list_users(self):
        """Lists users (<pwd> must be that of an admins' to use this).

        The callback function will receive the following data.
            {
                "type": "list users",
                "text": <str>; online users
            }
        """
        self._send_packet({"cmd": "listUsers"})

    def broadcast(self, text):
        """Sends <text> (<str>) to hack.chat.

        <pwd> must be that of an admins' to use this.

        The following data will be sent to the callback function.
            {
                "type": "broadcast",
                "text": <str>; the message broadcasted
            }
        """
        self._send_packet({"cmd": "broadcast", "text": text})

    def leave(self):
        """Leaves the channel currently connected to."""
        self._thread = False
        self._ws.close()
