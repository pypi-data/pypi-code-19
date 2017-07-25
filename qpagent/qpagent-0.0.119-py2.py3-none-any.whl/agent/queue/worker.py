#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

from agent.worker.macaca import Macaca
from agent.queue import q

logger = logging.getLogger(__name__)


def handle_task():
    while True:
        try:
            data = q.get(timeout=3000)
            if data:
                agent_task = json.load(data)
                print(agent_task)
                worker_type = agent_task['worker_type']
                worker_data = agent_task['worker_data']
                if worker_type == 1:
                    Macaca(worker_data).run()
        except BaseException as e:
            logger.exception(e)
