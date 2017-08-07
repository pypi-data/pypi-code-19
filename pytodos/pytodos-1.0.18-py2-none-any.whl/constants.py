# coding:utf-8
from enum import Enum


class ShowInfo(Enum):
    ADDED = 0
    EXIST = 1
    NOT_STARTED = 2
    DOING = 3
    DONE = 4
    ALL = 5


class TaskStatus(Enum):
    NOT_STARTED = 0
    DOING = 1
    DONE = 2
