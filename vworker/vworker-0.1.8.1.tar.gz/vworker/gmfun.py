#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gearman
from gearman.errors import GearmanError
import logging
import ujson
import time
from .config import config

log = logging.getLogger(__name__)

class Gmfun(object):

    def __init__(self, host_list, log_host_list):
        self.host_list = host_list
        self.log_host_list = log_host_list

    def _now_time(self):
        """ 当前UTC时间戳
        """
        return int(time.time() * 1000)


    def send_then_wait(self, job_name, job_data):
        gm = None
        try:
            seqnum = job_data.get("seqnum", self._now_time())
            job_data['seqnum'] = seqnum
            job_data['web_st'] = self._now_time()

            job_json = ujson.dumps(job_data, ensure_ascii=False)

            gm = gearman.GearmanClient(self.host_list)
            job = gm.submit_job(str(job_name), job_json, poll_timeout=30)

            if job.complete:
                rtnmap = ujson.loads(job.result)

                # 日志记录到elastic search
                log_map = {}
                log_map['fun'] = job_name
                log_map['et'] = self._now_time()
                log_map['in'] = job_data
                log_map['out'] = rtnmap

                self._send_only_for_log('es_idx_log', log_map)

                try:
                    del rtnmap['ip']
                    del rtnmap['Git_HEAD']
                    del rtnmap['user_ip']
                    del rtnmap['seqnum']
                    del rtnmap['web_st']
                    del rtnmap['user_agent']
                except Exception as e:
                    log.error(e, exc_info=True)

                return rtnmap
            else:
                tmp = "{}: timeout".format(job_name)
                data = {'status': 110, 'seqnum': seqnum, 'msg': tmp}
                return data
        except Exception as e:
            log.error(e, exc_info=True)
            data = {'status': 998, 'seqnum': self._now_time(), 'msg': e}
            return data
        finally:
            if gm:
                gm.shutdown()


    def send_only(self, job_name, job_data):
        gm = None
        try:
            job_data['seqnum'] = job_data.get("seqnum", self._now_time())
            job_data['web_st'] = job_data.get("web_st", self._now_time())

            gm = gearman.GearmanClient(self.host_list)
            job_json = ujson.dumps(job_data, ensure_ascii=False)
            gm.submit_job(str(job_name), job_json, background=True, wait_until_complete=False)
        except Exception as e:
            log.error(e, exc_info=True)
            data = {'status': 998, 'seqnum': self._now_time(), 'msg': e}
            return data
        finally:
            if gm:
                gm.shutdown()


    def _send_only_for_log(self, job_name, job_data):
        gm = None
        try:
            # 这里用的是es_log的gearman
            gm = gearman.GearmanClient(self.log_host_list)
            job_json = ujson.dumps(job_data, ensure_ascii=False)
            gm.submit_job(str(job_name), job_json, background=True, wait_until_complete=False)
        except GearmanError as e:
            log.error(e, exc_info=True)
            data = {'status': 998, 'seqnum': self._now_time(), 'msg': e}
            return data
        finally:
            if gm:
                gm.shutdown()


gmfun = Gmfun(config['gearman'].split(';'), config['gearman_log'].split(';'))
