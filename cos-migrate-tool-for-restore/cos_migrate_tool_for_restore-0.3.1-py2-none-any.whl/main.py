# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pkg_resources
from ConfigParser import SafeConfigParser
from logging import getLogger, basicConfig, DEBUG
from sys import stderr
from argparse import ArgumentParser
import os
from os import path

from Queue import Empty, Full
import multiprocessing
import os
import time

from migrate_tool.migrator import ThreadMigrator

import signal
from logging.config import dictConfig
from threading import Thread
import sys
reload(sys)
sys.setdefaultencoding('utf8')


log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(filename)s:%(lineno)s - %(process)d - %(name)s - %(message)s'
        },
        'error': {
            'format': '%(asctime)s\t%(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'error_file': {
            'level': 'INFO',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': 'fail_files.txt',
            'mode': 'a'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'migrate_tool.fail_file': {
            'handlers': ['error_file'],
            'level': 'WARN',
            'propagate': False
        },
        'requests.packages': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': True
        }
    }
}


services_ = {}


def loads_services():
    global services_
    for ep in pkg_resources.iter_entry_points(group='storage_services'):
        services_.update({ep.name: ep.load()})


def create_parser():
    parser_ = ArgumentParser()
    parser_.add_argument('-c', '--conf', type=file, required=True, help="specify your config")
    return parser_


def main_thread():
    parser = create_parser()
    opt = parser.parse_args()
    conf = SafeConfigParser()
    conf.readfp(opt.conf)

    output_service_conf = dict(conf.items('source'))
    input_service_conf = dict(conf.items('destination'))
    if conf.has_option('common', 'threads'):
        _threads = conf.getint('common', 'threads')
    else:
        _threads = 10
    workspace_ = conf.get('common', 'workspace')
    try:
        os.makedirs(workspace_)
    except OSError:
        pass

    log_config['handlers']['error_file']['filename'] = path.join(workspace_, 'failed_files.txt')
    dictConfig(log_config)

    loads_services()
    output_service = services_[output_service_conf['type']](**output_service_conf)
    input_service = services_[input_service_conf['type']](**input_service_conf)
    work_dir = conf.get('common', 'workspace')

    # init share queue
    share_queue = multiprocessing.Queue()
    lock = multiprocessing.Lock()

    # init restore process
    restore_process = multiprocessing.Process(target=restore_check_thread,
                                              args=(share_queue, lock, work_dir, output_service, input_service))
    restore_process.start()

    # init work process pool
    threads_pool = []
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=work_thread,
                                    args=(share_queue, lock, work_dir, output_service, input_service))
        threads_pool.append(p)
    start_pool(threads_pool)

    # todo, stop restore process
    restore_process.join()

    # todo, stop worker process
    stop_pool(threads_pool)
    pass


def restore_check_thread(share_queue, lock, work_dir, output_service, input_service):
    migrator = ThreadMigrator(input_service=input_service,
                              output_service=output_service,
                              work_dir=work_dir,
                              threads=10,
                              share_q=share_queue)
    migrator.start()
    pass

logger = getLogger(__name__)
fail_logger = getLogger('migrate_tool.fail_file')
pool_stop = False


def start_pool(threads_pool):
    logger.info("multiprocessing thread pool is staring")
    for p in threads_pool:
        p.start()
    logger.info("multiprocessing thread pool staring done")


def stop_pool(threads_pool):
    logger.info("multiprocessing thread pool join begin")
    global pool_stop
    pool_stop = True
    for p in threads_pool:
        p.join()
    logger.info("multiprocessing thread pool join done")


def work_thread(share_queue, lock, work_dir, output_service, input_service):
    logger.info("multiprocessing pool worker is starting")
    while True:
        global pool_stop
        if pool_stop:
            logger.info("pool_stop is true, work process: %d, will exit", os.getpid())
            break
        # logger.info("worker stop: " + str(self._stop))
        try:
            # logger.debug("try to get task")
            logger.info("get one task from share queue begin")
            task = share_queue.get_nowait()
            # logger.debug("get task succeefully")
            share_queue.task_done()
        except Empty:
            logger.info("task queue is empty, will sleep 3 seconds")
            time.sleep(3)
            continue

        logger.info("get one task from share queue end, task: %s", task.key)

        task_path = task.key
        if task_path.startswith('/'):
            task_path = task_path[1:]

        if isinstance(task_path, str):
            task_path = task_path.decode('utf-8')

        import uuid
        localpath = unicode(path.join(work_dir, uuid.uuid1().hex))

        try:
            try:
                os.makedirs(path.dirname(localpath))
            except OSError as e:
                # directory is exists
                logger.debug(str(e))

            try:
                ret = input_service.exists(task)
                if ret:
                    logger.info("{file_path} exists".format(file_path=task_path.encode('utf-8')))
                    # with lock:
                    #     succ += 1
                    #     filter.add(task_path)
                    continue
            except Exception as e:
                logger.exception("exists failed")

            try:
                output_service.download(task, localpath)
            except Exception as e:
                logger.exception("download failed")
                # with lock:
                #     fail += 1
                fail_logger.error(task_path)
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

            logger.info("remove task: %s, size: %d, file local path: %s, success", task.key, task.size,
                        localpath)

            if isinstance(task_path, unicode):
                logger.info("inc succ with {}".format(task_path.encode('utf-8')))
            else:
                logger.info("inc succ with {}".format(task_path.encode('utf-8')))

            # with lock:
            #     add task to filter
            #     succ += 1
            #     filter.add(task_path)
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
    logger.info("multiprocessing pool worker: %d, will exit", os.getpid())


def main_():
    thread_ = Thread(target=main_thread)
    thread_.daemon = True
    thread_.start()
    try:
        while thread_.is_alive():
            thread_.join(2)
    except KeyboardInterrupt:
        print 'exiting'


if __name__ == '__main__':
    main_()
