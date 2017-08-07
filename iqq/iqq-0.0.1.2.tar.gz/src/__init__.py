#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Muduo
'''
    Fast Sync
'''
import sys
import argparse
import qqbot

def print_version():
    print('''\033[32m
            + ------------------------------------------ +
            |                iQQ 0.0.1.2 is free         |
            + ------------------------------------------ +
            |                                            |
            |    ☺  -------------------------->  ☺       |
            |                                            |
            |   You could donate to the Alipay account   |
            |                                            |
            |            49668929@qq.com                 |
            |                                            |
            |         ~~~~Thank you!~~~~~~~              |
            |                                            |
            |            Author : Muduo                  |
            |                                            |
            + ------------------------------------------ +
    \033[0m''')


print_version()

def login():
    parser = argparse.ArgumentParser()
    parser.add_argument('qq',
                        type=str,
                        help='qq账号')
    parser.add_argument('kb',
                        type=str,
                        help='知识库')

    args = parser.parse_args()

    main(args.qq, args.kb)

def main(qq, kb):

    @qqbot.qqbotslot
    def onQQMessage(bot, contact, member, content):
        has_match = False
        for kr in open(kb, 'r').read().split('\n\n\n'):
            arr = kr.strip().split('\n', 1)
            if len(arr) != 2:
                continue

            keyword, reply = arr
            if keyword == '*' and not has_match:
                bot.SendTo(contact, reply)
            elif content.find(keyword) != -1:
                bot.SendTo(contact, reply)
                has_match = True

    qqbot._bot.Login([
        '-q', qq,
        '-cq',
    ])
    qqbot._bot.Run()
