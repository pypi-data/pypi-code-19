#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import time

from agent.worker.macaca import Macaca
from agent.queue import q
from ..consts import AgentWorkerType
from agent.qualityplatform.agent import get_task_by_id

logger = logging.getLogger(__name__)


def handle_task():
    while True:
        try:
            data = q.get(timeout=3000)
            if data:
                agent_task = json.load(data)
                task = get_task_by_id(agent_task.get('task_id'))
                worker_data = json.loads(task.get('params'))
                worker_type = worker_data.get('worker_type')
                if worker_type is AgentWorkerType.macaca.value:
                    Macaca(worker_data).run()
        except BaseException as e:
            logger.exception(e)
