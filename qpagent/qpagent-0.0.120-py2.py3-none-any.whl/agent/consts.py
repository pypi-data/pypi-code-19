#!/usr/bin/env python
# -*- coding: utf-8 -*-
import enum


class AgentWorkerType(enum.IntEnum):
    unknown = 0
    macaca = 1


class TaskType(enum.IntEnum):
    unknown = 0
    crawler = 1
    classify = 2
    esm = 3
    proxy = 4
    uiplay = 5
    uirecord = 6
