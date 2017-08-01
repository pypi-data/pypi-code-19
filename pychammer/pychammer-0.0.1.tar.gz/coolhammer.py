#!/usr/bin/env python
# -*- encoding: utf-8 -*-


def show_hammer():
    print('This is show_hammer function.')


class CoolHammer():
    def __init__(self):
        self.str = "Hello, CoolHammer!"

    def print_log(self):
        print(self.str)

    def print_blog(self):
        print(self.str.swapcase())




