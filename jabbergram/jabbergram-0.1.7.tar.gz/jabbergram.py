#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import logging
from sys import argv
from threading import Thread
from time import sleep
from xml.dom import minidom

import sleekxmpp
import telegram
from sleekxmpp.xmlstream.stanzabase import ElementBase
from telegram.error import NetworkError, Unauthorized


try:
    import requests
except:
    logging.error("HTTP Upload support disabled.")


class Request(ElementBase):
    """Special class to create http_upload requests."""
    namespace = 'urn:xmpp:http:upload'
    name = 'request'
    plugin_attrib = 'request'
    interfaces = set(('filename', 'size'))
    sub_interfaces = interfaces


class Jabbergram(sleekxmpp.ClientXMPP):
    """Main object."""
    def __init__(self, jid, password, rooms, nick, token, groups, verify_ssl):
        """
        Executed when the class is initialized. It adds session handlers, muc
        handlers and send the telegram reading function and the HTTP upload
        initializing functions to their respective threads.
        """
        # XMPP
        super(Jabbergram, self).__init__(jid, password)
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('groupchat_message', self.muc_message)

        self.muc_rooms = rooms.split()
        self.nick = nick
        self.token = token
        self.xmpp_users = {}
        self.jid = jid
        self.verify_ssl = verify_ssl

        for muc in self.muc_rooms:
            self.add_event_handler("muc::%s::got_online" % muc,
                                   self.muc_online)
            self.add_event_handler("muc::%s::got_offline" % muc,
                                   self.muc_offline)

        # Telegram
        self.groups = groups.split()
        self.bot = telegram.Bot(self.token)
        self.telegram_users = {}

        # initialize http upload on a thread since its needed to be connected
        # to xmpp
        t = Thread(target=self.init_http)
        t.daemon = True
        t.start()

        # put tg connector in a thread
        t = Thread(target=self.read_tg)
        t.daemon = True
        t.start()

        print('Please wait a couple of minutes until it\'s correctly '
              'connected')

    def init_http(self):
        """
        Initializes HTTP upload support. Sends a discovery stanza to the server
        to find the HTTP upload component and asks for the max size a file can
        be.
        """
        self.http_upload = self.HttpUpload(self)
        self.component = self.http_upload.discovery()

        if self.component:
            xml = self.http_upload.disco_info(self.component)
            xml = minidom.parseString(str(xml))
            self.max_size = int(xml.getElementsByTagName('value')
                                [1].firstChild.data)
        else:
            try:
                self.component = self.jid.split('@')[1]
                xml = self.http_upload.disco_info(self.component)
                xml = minidom.parseString(str(xml))
                self.max_size = int(xml.getElementsByTagName('value')
                                    [1].firstChild.data)
            except:
                self.max_size = None

    def read_tg(self):
        """Main telegram function."""
        update_id = 0

        # wait until http_upload has been tested
        sleep(5)
        while True:
            try:
                for update in self.bot.getUpdates(offset=update_id,
                                                  timeout=10):
                    name = ''
                    size = 0

                    if update.edited_message:
                        update_id = update.update_id + 1
                        continue

                    if update.message.from_user:
                        user = update.message.from_user.username

                        # sometimes there's no user. weird, but it happens
                        if not user:
                            user = update.message.from_user.first_name

                    # sometimes there's no user. weird, but it happens
                    elif update.message['from']:
                        user = str(update.message['from'].first_name)

                    if update.message.audio or update.message.document or \
                       update.message.photo or update.message.video \
                       or update.message.voice or update.message.sticker:
                        # proceed only if http upload is available

                        if self.max_size is not None:
                            if update.message.audio:
                                d_file = update.message.audio
                                ext = '.ogg'
                                size = d_file.file_size
                            elif update.message.document:
                                d_file = update.message.document
                                ext = ''
                                size = d_file.file_size
                            elif update.message.photo:
                                d_file = update.message.photo[-1]
                                ext = '.jpg'
                                size = d_file.file_size
                            elif update.message.video:
                                d_file = update.message.video[-1]
                                ext = '.mp4'
                                size = d_file.file_size
                            elif update.message.voice:
                                d_file = update.message.voice
                                ext = '.ogg'
                                size = d_file.file_size
                            elif update.message.sticker:
                                d_file = update.message.sticker
                                ext = '.png'
                                size = d_file.file_size
                            if self.max_size >= int(size):
                                t_file = self.bot.getFile(d_file.file_id)
                                f_name = '/tmp/' + d_file.file_id + ext
                                t_file.download(f_name)
                                url = self.http_upload.upload(
                                    self.component,
                                    self.verify_ssl,
                                    f_name, size)

                                if update.message.caption:
                                    message = update.message.caption + ' '
                                else:
                                    message = 'File uploaded: '

                                message += url
                            else:
                                message = 'A file has been uploaded to Telegr'\
                                          'am, but is too big.'
                        else:
                            message = 'A file has been uploaded to Telegram,'\
                                      'but the XMPP server doesn\'t support H'\
                                      'TTP Upload.'

                    elif update.message.new_chat_members:
                        message = 'This user has joined the group.'
                    elif update.message.left_chat_member:
                        message = 'This user has left the group.'
                    elif update.message.new_chat_title:
                        message = 'The group\'s title has changed: ' + \
                          update.message.new_chat_title
                    elif update.message.new_chat_photo:
                        message = 'The group\'s photo has changed.'
                    else:
                        if update.message.reply_to_message:
                            name = update.message.reply_to_message.from_user\
                                                                  .username
                            if name != self.bot.username:
                                message = name + ': ' + \
                                          update.message.reply_to_message.text
                            else:
                                message = update.message.reply_to_message.text
                        else:
                            message = update.message.text

                    if name:
                        msg = message + ' <- ' + user + ": " + \
                              update.message.text
                    else:
                        msg = user + ": " + message

                    if update.message.chat.type == 'supergroup' and \
                       update.message.chat.username:
                        chat = '@' + update.message.chat.username
                    else:
                        chat = str(update.message.chat.id)

                    if chat not in self.groups:
                        chat = str(update.message.chat_id)

                    if message and chat in self.groups:
                        index = self.groups.index(chat)
                        receiver = self.muc_rooms[index]

                        if chat in self.telegram_users:
                            if user not in self.telegram_users[chat]:
                                self.telegram_users[chat] += ' ' + user
                        else:
                            self.telegram_users[chat] = ' ' + user

                        if message == '.users':
                            self.say_users('telegram', receiver, chat)
                        elif message == '.help':
                            self.say_help('telegram', receiver, chat)
                        elif message == '.where':
                            self.say_where('telegram', receiver, chat)
                        else:
                            self.send_message(mto=receiver, mbody=msg,
                                              mtype='groupchat')
                    update_id = update.update_id + 1

            except NetworkError as e:
                print(e)
                sleep(1)

            except Unauthorized as e:
                print(e)
                sleep(1)

            except Exception as e:
                update_id += 1
                print(e)

    def start(self, event):
        """Does some initial setup for XMPP and joins all mucs."""
        self.get_roster()
        self.send_presence()

        for muc in self.muc_rooms:
            self.plugin['xep_0045'].joinMUC(muc, self.nick, wait=True)

    def muc_message(self, msg):
        """Muc message's handler."""
        muc_room = str(msg['from']).split('/')[0]
        index = self.muc_rooms.index(muc_room)
        tg_group = self.groups[index]

        if msg['body'] == '.users':
            self.say_users('xmpp', muc_room, tg_group)
        elif msg['body'] == '.help':
            self.say_help('xmpp', muc_room, tg_group)
        elif msg['body'] == '.where':
            self.say_where('xmpp', muc_room, tg_group)
        elif msg['mucnick'] != self.nick:
            message = str(msg['from']).split('/')[1] + ': ' + str(msg['body'])
            self.bot.sendMessage(tg_group, text=message)

    def muc_online(self, presence):
        """Muc presence's handler."""
        user = presence['muc']['nick']
        muc = presence['from'].bare

        if user != self.nick:
            if muc in self.xmpp_users:
                self.xmpp_users[muc].append(presence['muc']['nick'])
            else:
                self.xmpp_users[muc] = [presence['muc']['nick']]

    def muc_offline(self, presence):
        """Muc presence's handler."""
        user = presence['muc']['nick']
        muc = presence['from'].bare

        if user != self.nick:
            self.xmpp_users[muc].remove(presence['muc']['nick'])

    def say_users(self, service, muc, group):
        """It returns the users on XMPP or Telegram."""
        if service == 'xmpp':
            if group in self.telegram_users:
                tg_users = self.telegram_users[group]
            else:
                tg_users = ""

            msg = 'Telegram Users:' + tg_users

            self.send_message(mto=muc, mbody=msg, mtype='groupchat')

        elif service == 'telegram':
            xmpp_users = ""
            if muc in self.xmpp_users:
                for i in self.xmpp_users[muc]:
                    xmpp_users = xmpp_users + ' ' + i
            else:
                xmpp_users = ""

            msg = 'XMPP Users:' + xmpp_users
            self.bot.sendMessage(group, text=msg)

    def say_help(self, service, muc, group):
        """Help command."""
        msg = 'Hi, I\'m ' + self.bot.username + '. I have two commands : ".us'\
              'ers" and ".where".'
        if service == 'xmpp':
            self.send_message(mto=muc, mbody=msg, mtype='groupchat')
        elif service == 'telegram':
            self.bot.sendMessage(group, text=msg)

    def say_where(self, service, muc, group):
        """Returns Telegram's group location if it's public."""
        if service == 'xmpp':
            if '@' in group:
                msg = 'I\'m on http://telegram.me/' + group.split('@')[1] + '.'
            else:
                msg = 'Sorry, I\'m on a private group, you\'ll have to ask fo'\
                      'r an invitation.'
            self.send_message(mto=muc, mbody=msg, mtype='groupchat')
        elif service == 'telegram':
            msg = 'I\'m on ' + muc + '.'
            self.bot.sendMessage(group, text=msg)

    class HttpUpload():
        """HTTP upload main class."""
        def __init__(self, parent_self):
            """Init... Yep."""
            self.parent_self = parent_self

        def discovery(self):
            """Discovers all server's components."""
            disco = sleekxmpp.basexmpp.BaseXMPP.Iq(self.parent_self)
            disco['query'] = "http://jabber.org/protocol/disco#items"
            disco['type'] = 'get'
            disco['from'] = self.parent_self.jid
            disco['to'] = self.parent_self.jid.split('@')[1]

            d = disco.send(timeout=30)
            xml = minidom.parseString(str(d))
            item = xml.getElementsByTagName('item')

            for component in item:
                component = component.getAttribute('jid')
                info = self.disco_info(component)

                if "urn:xmpp:http:upload" in info:
                    http_upload_component = component
                    break
                else:
                    http_upload_component = ""

            return http_upload_component

        def disco_info(self, component):
            """Discovers HTTP upload components attributes."""
            info = sleekxmpp.basexmpp.BaseXMPP.Iq(self.parent_self)
            info['query'] = "http://jabber.org/protocol/disco#info"
            info['type'] = 'get'
            info['from'] = self.parent_self.jid
            info['to'] = component
            response = str(info.send(timeout=30))

            return response

        def upload(self, component, verify_ssl, u_file, size):
            """Uploads to HTTP upload."""
            peticion = Request()
            peticion['filename'] = u_file.split('/')[-1]
            peticion['size'] = str(size)

            iq = sleekxmpp.basexmpp.BaseXMPP.Iq(self.parent_self)
            iq.set_payload(peticion)
            iq['type'] = 'get'
            iq['to'] = component
            iq['from'] = self.parent_self.jid

            send = iq.send(timeout=30)

            xml = minidom.parseString(str(send))
            put_url = xml.getElementsByTagName('put')[0].firstChild.data

            if verify_ssl == 'False':
                req = requests.put(put_url, data=open(u_file, 'rb'),
                                   verify=False)
            else:
                req = requests.put(put_url, data=open(u_file, 'rb'))

            return put_url


if __name__ == '__main__':

    # parse config
    config = []
    parser = configparser.SafeConfigParser()

    if len(argv) == 2:
        parser.read(argv[1])
    else:
        parser.read('config.ini')

    for name, value in parser.items('config'):
        config.append(value)

    # assign values for the bot
    jid = config[0]
    password = config[1]
    muc_rooms = config[2]
    nick = config[3]
    token = config[4]
    groups = config[5]
    verify_ssl = config[6]

    xmpp = Jabbergram(jid, password, muc_rooms, nick, token, groups,
                      verify_ssl)
    xmpp.register_plugin('xep_0045')

    if xmpp.connect():
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
