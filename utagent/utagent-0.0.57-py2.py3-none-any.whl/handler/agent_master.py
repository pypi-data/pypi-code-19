#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

from slave.globalvar import get_queue
from slave.config import config
from macaca_worker import MacacaWorker

logger = logging.getLogger(__name__)


def post_get(name, data):
    return data.get(name)


def handle_task():
    while True:
        try:
            data = get_queue().get(timeout=3000)
            if data:
                print(data)
                agent_task = json.loads(data)
                print(agent_task)
                worker_type = agent_task.get('worker_type')
                print(worker_type)
                worker_data = agent_task['worker_data']
                if worker_type == 1:
                    print('>>>>>>>>>>')
                    MacacaWorker(config["macaca_dir"], worker_data).run()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e.message)
            logger.exception(e)


# if __name__ == '__main__':
#     print(json.loads('%s' % {"worker_type":1,"worker_data":{"task_type":2}}))
