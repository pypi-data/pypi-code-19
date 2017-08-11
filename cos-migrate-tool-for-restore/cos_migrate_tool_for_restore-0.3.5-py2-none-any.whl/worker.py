# -*- coding:utf-8 -*-
from os import path, makedirs
from logging import getLogger
import time
from Queue import Empty, Full
import multiprocessing
import os
import uuid

from migrate_tool.filter import Filter


logger = getLogger(__name__)
fail_logger = getLogger('migrate_tool.fail_file')
pool_stop = False


def work_thread(share_queue, lock, work_dir, output_service, input_service):
    logger.info("multiprocessing pool worker is starting")
    _filter = Filter(work_dir)

    while True:
        global pool_stop
        if pool_stop:
            logger.info("pool_stop is true, work process: %d, will exit", os.getpid())
            break
        try:
            logger.info("get one task from task queue begin")
            task = share_queue.get_nowait()
        except Empty:
            logger.info("task queue is empty, will sleep 3 seconds")
            time.sleep(3)
            continue

        logger.info("get one task from task queue end, task: %s", task.key)

        task_path = task.key
        if task_path.startswith('/'):
            task_path = task_path[1:]
        if isinstance(task_path, str):
            task_path = task_path.decode('utf-8')

        localpath = unicode(path.join(work_dir, uuid.uuid1().hex))
        try:
            try:
                os.makedirs(path.dirname(localpath))
            except OSError as e:
                # directory is exists
                logger.warn(str(e))

            try:
                ret = input_service.exists(task)
                if ret:
                    logger.info("{file_path} exists, skip it".format(file_path=task_path.encode('utf-8')))
                    with lock:
                        filter.add(task_path)
                    continue
            except Exception as e:
                # todo, override ?
                logger.exception("exists failed")

            try:
                output_service.download(task, localpath)
            except Exception as e:
                logger.exception("download {} failed".format(task_path.encode('utf-8')))
                fail_logger.error(task_path)
                # with lock:
                #     fail += 1
                continue
            logger.info("download task: %s, size: %d, to local path: %s, success", task.key, task.size,
                        localpath)

            try:
                input_service.upload(task, localpath)
            except Exception:
                logger.exception("upload {} failed".format(task_path.encode('utf-8')))
                # with lock:
                #     fail += 1
                fail_logger.error(task_path)
                continue
            logger.info("upload task: %s, size: %d, from local path: %s, success", task.key, task.size,
                        localpath)

            try:
                if isinstance(localpath, unicode):
                    localpath = localpath.encode('utf-8')
                os.remove(localpath)
                try:
                    os.removedirs(path.dirname(localpath))
                except OSError:
                    pass
            except Exception as e:
                logger.exception(str(e))
                continue
            logger.info("remove task: %s, size: %d, file local path: %s, success", task.key, task.size,
                        localpath)
            if isinstance(task_path, unicode):
                logger.info("inc succ with {}".format(task_path.encode('utf-8')))
            else:
                logger.info("inc succ with {}".format(task_path.encode('utf-8')))

            with lock:
                # add task to filter
                # succ += 1
                filter.add(task_path)
        except Exception:
            logger.exception("try except for deleting file")

        finally:
            if isinstance(localpath, unicode):
                localpath = localpath.encode('utf-8')
            try:
                os.remove(localpath)
                os.removedirs(path.dirname(localpath))
            except OSError:
                pass
    logger.info("multiprocessing pool worker: %d, will exit", os.getpid())


