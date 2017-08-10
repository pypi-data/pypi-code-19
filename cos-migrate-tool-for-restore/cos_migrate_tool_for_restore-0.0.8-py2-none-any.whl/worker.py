# -*- coding:utf-8 -*-
from os import path, makedirs
from logging import getLogger
import time
from Queue import Empty, Full
import multiprocessing


logger = getLogger(__name__)
fail_logger = getLogger('migrate_tool.fail_file')


class Worker(object):
    def __init__(self, work_dir, file_filter, input_service, output_service, threads_num=5, max_size=30):
        self._input_service = input_service
        self._output_service = output_service
        self._filter = file_filter
        self._work_dir = work_dir

        self._threads_num = threads_num
        self._threads_pool = []
        # todo， set maxsize to 0
        self._queue = multiprocessing.JoinableQueue()
        self._threads_pool = multiprocessing.Pool(processes=self._threads_num)

        self._stop = False
        self._succ = 0
        self._fail = 0
        self._lock = multiprocessing.Lock()

    def __work_thread(self, queue):

        while not self._stop:
            # logger.info("worker stop: " + str(self._stop))
            try:
                # logger.debug("try to get task")
                task = self._queue.get()
                # logger.debug("get task succeefully")
                self._queue.task_done()
            except Empty:
                logger.debug("Empty queue, will sleep 1 second, stop flag: " + str(self._stop))
                if self._stop:
                    break
                else:
                    time.sleep(1)
                    continue
            logger.info("get one task from share queue, task: %s", task.key)

            task_path = task.key
            if task_path.startswith('/'):
                task_path = task_path[1:]

            if isinstance(task_path, str):
                task_path = task_path.decode('utf-8')

            import uuid
            localpath = unicode(path.join(self._work_dir, uuid.uuid1().hex))

            try:
                try:
                    makedirs(path.dirname(localpath))
                except OSError as e:
                    # directory is exists
                    logger.debug(str(e))

                try:
                    ret = self._input_service.exists(task)
                    if ret:
                        logger.info("{file_path} exists".format(file_path=task_path.encode('utf-8')))
                        with self._lock:
                            self._succ += 1
                            self._filter.add(task_path)
                        continue
                except Exception as e:
                    logger.exception("exists failed")

                try:
                    self._output_service.download(task, localpath)
                except Exception as e:
                    logger.exception("download failed")
                    with self._lock:
                        self._fail += 1
                    fail_logger.error(task_path)
                    continue

                logger.info("download task: %s, size: %d, to local path: %s, success", task.key, task.size, localpath)

                try:
                    self._input_service.upload(task, localpath)
                except Exception:
                    logger.exception("upload {} failed".format(task_path.encode('utf-8')))
                    with self._lock:
                        self._fail += 1
                    fail_logger.error(task_path)
                    continue

                logger.info("upload task: %s, size: %d, from local path: %s, success", task.key, task.size, localpath)

                try:
                    import os
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

                logger.info("remove task: %s, size: %d, file local path: %s, success", task.key, task.size, localpath)

                if isinstance(task_path, unicode):
                    logger.info("inc succ with {}".format(task_path.encode('utf-8')))
                else:
                    logger.info("inc succ with {}".format(task_path.encode('utf-8')))

                with self._lock:
                    # add task to filter
                    self._succ += 1
                    self._filter.add(task_path)
            except Exception:
                logger.exception("try except for deleting file")

            finally:
                    import os
                    if isinstance(localpath, unicode):
                        localpath = localpath.encode('utf-8')

                    try:
                        os.remove(localpath)
                        os.removedirs(path.dirname(localpath))
                    except OSError:
                        pass

    def add_task(self, task):
        # blocking
        self._queue.put(task)

    def start(self):
        self._threads_pool.apply_async(self.__work_thread, self._queue)
        self._threads_pool.close()
        self._threads_pool.join()

    def stop(self):
        self._queue.join()
        self.term()

    def term(self):
        self._stop = True
        logger.info("try to stop migrate process.")
        # while any([t.is_alive() for t in self._threads_pool]):
        #     map(lambda i: i.join(5), filter(lambda j: j.is_alive(), self._threads_pool))
        #     print filter(lambda j: j.is_alive(), self._threads_pool)
        self._threads_pool.terminate()

    @property
    def success_num(self):
        return self._succ

    @property
    def failure_num(self):
        return self._fail
