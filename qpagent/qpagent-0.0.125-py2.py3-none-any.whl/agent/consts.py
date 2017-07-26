#!/usr/bin/env python
# -*- coding: utf-8 -*-
import enum


class AgentWorkerType(enum.IntEnum):
    unknown = 0
    macaca = 1


class TaskType(enum.IntEnum):
    unknown = 0
    uiplay = 1
    uirecord = 2
