#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

from agent.globalvar import get_queue
from agent.config import config
from agent.util.file import File_Downloader
from mobile_uirecorder_worker import MobileUiRecorderWorker
from pc_uirecorder_worker import PCUiRecorderWorker

logger = logging.getLogger(__name__)


def post_get(name, data):
    return data.get(name)


def handle_task():
    while True:
        try:
            data = get_queue().get(timeout=3000)
            if data:
                agent_task = json.load(data)
                worker_type = agent_task['worker_type']
                worker_data = agent_task['worker_data']
                if worker_type == 1:
                    MobileUiRecorderWorker(File_Downloader.get_work_space(config["macaca_dir"] + '/mobile.uirecorder'),
                                           worker_data).run()
                elif worker_type == 2:
                    PCUiRecorderWorker(File_Downloader.get_work_space(config["macaca_dir"] + '/pc.uirecorder'),
                                       worker_data).run()
        except BaseException:
            pass
