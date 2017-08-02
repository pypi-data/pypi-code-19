#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import gearman
import inspect
import ujson

from pyfiglet import Figlet

from .userdata import usercard
from .config import config
from .redisfun import redisfun
from .monitoring import monitor_worker_ok
import tools

from logging import getLogger
logger = getLogger(__name__)


class frame(object):

    def __init__(self, worker_name, gm_host_list=None, clinent_id=None, plugin_path=None):
        """
        :gm_host_list: Gearman host list
        :plugin_path: 插件路径
        :task_list: 已注册的 task 列表,用来判断 task 名是否冲突
        """

        if clinent_id is None:
            random_id_lst = ['gm_worker_']
            random_id_lst.extend([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(8)])
            clinent_id = ''.join(random_id_lst)

        gm_host_list = gm_host_list or config['gearman'].split(';')

        self.worker_name = worker_name
        self.gm_host_list = gm_host_list
        self.clinent_id = clinent_id
        self.plugin_path = plugin_path or 'worker'
        self.plugin_list = []
        self.task_list = {}

    def _package_data(self, data=None, status=None, msg=None, do_ms=None):
        """ 在外面包裹一层
        :data:
        :status:
        :return: -> dict
            {'body': data, # if data True
            'status': 200,
            'msg': 'ok',
            'seqnum': now_time()}
        """
        if not status:
            status = 200
        if not msg:
            msg = 'ok'

        structure = {
            'status': status,
            'ip': config['g_ip'],
            'do_ms': do_ms or 0,
            'msg': msg,
            'seqnum': tools.now_time()
        }

        if config['debug']:
            structure['Git_HEAD'] = config['git_version']

        if not data is None:
            structure['body'] = data
        return structure

    def _loadreq(self, data):
        """
        加载请求
        """
        req = ujson.loads(data)
        # 扔掉
        req.pop('user_ip', '')
        req.pop('seqnum', '')
        req.pop('web_st', '')
        req.pop('user_agent', '')
        return req

    def _usercard_update(self, mysess):
        """
        更新用户登录信息
        """
        userdata_str = redisfun.get_sess_str(mysess)
        if userdata_str:
            userdata = ujson.loads(userdata_str)
            userdata['mysess'] = mysess
        else:
            userdata = {}
        # 更新用户登录信息
        usercard.update(userdata)

    def _handle_arg(self, req, task_obj):
        """
        处理参数
        """
        argspec = inspect.getargspec(task_obj)
        if argspec.defaults:
            # 必选参数 =  全部参数[ :-有默认值的参数的数量]
            required = argspec.args[:-len(argspec.defaults)]
        else:
            required = argspec.args
        # 如果入参和必选参数的交集不等于必选参数
        if set(req) & set(required) != set(required):
            if config['debug']:
                absent = set(required) - set(req)
                raise ValueError(618, u'缺少主要参数 {}'.format(' '.join(absent)))
            else:
                raise ValueError(618, u'缺少主要参数')
        # 如果有可变参数 直接塞进去就好了
        if argspec.keywords:
            kw = req
        else:
            kw = {}
            for x in argspec.args:
                args = req.get(x, None)
                if args is None:
                    continue
                kw[x] = args
        return kw

    def reg_gm_task(self, task_name, task_obj):
        """注册 task 工具.

        :worker_name: 注册 warker 时的名字
        :worker_obj:  传递的函数对象
        """
        def task_wrapper(worker, job):
            body = {}
            try:
                req = self._loadreq(job.data)
                mysess = req.pop('mysess', '')
                # 更新用户登录信息
                self._usercard_update(mysess)
                # 获取参数
                kw = self._handle_arg(req, task_obj)
                # 执行函数
                logger.debug("input: %s", kw)
                b_time = tools.now_time()
                return_data = task_obj(**kw)
                e_time = tools.now_time()
                logger.debug("output: %s", return_data)
                do_ms = e_time - b_time

                # return ujson.dumps(return_data, ensure_ascii=False)
                if return_data is None:
                    body['data'] = {}
                else:
                    body['data'] = return_data

                body['do_ms'] = do_ms
                return ujson.dumps(self._package_data(**body), ensure_ascii=False)
            except Exception as e:
                if len(e.args) >= 2:
                    body['status'] = e.args[0]
                    body['msg'] = e.args[1]
                else:
                    body['status'] = 999
                    body['msg'] = e.args[0]

                logger.error(body['msg'], exc_info=True)
                return ujson.dumps(self._package_data(**body), ensure_ascii=False)

        self.gm_wk.register_task(task_name, task_wrapper)

    def _load_plugin(self):
        """加载插件的方法
        """
        assert os.path.isdir(self.plugin_path), '未找到插件目录'
        self.plugin_list.extend([plugin for plugin in os.listdir(self.plugin_path)
                                 if os.path.isdir('/'.join([self.plugin_path, plugin]))
                                 if os.path.isfile('/'.join([self.plugin_path, plugin, 'main.py']))
                                 ])

        assert self.plugin_list, '未找到插件'
        # 遍历插件路径下的插件
        for plugin in self.plugin_list:
            # 加载 worker.plugin.main
            submodule = __import__('.'.join([self.plugin_path, plugin, 'main']))
            # 获得 worker.plugin.main 对象
            submodule_obj = getattr(submodule, plugin).main
            submodule_func = [
                # 列出对象中的函数和导入的模块
                func for func in dir(submodule_obj)
                # 忽略私有函数
                if func[0] != '_'
                # 确认是函数而不是模块
                if hasattr(getattr(submodule_obj, func), '__call__')
                # 确认是本地模块而不是第三方模块
                if getattr(getattr(submodule_obj, func), '__module__').split('.')[:2] == [self.plugin_path, plugin]
            ]
            assert submodule_func, '没有可加载的 task'
            # 遍历函数
            for func in submodule_func:
                # 函数对象
                task_obj = getattr(submodule_obj, func)
                # 函数名作为 task 名
                task_name = task_obj.__name__
                # 如果和已注册的 task 同名
                if task_name in self.task_list:
                    print u'{} is existed in the {}'.format(task_name, self.task_list[task_name])
                else:
                    # 注册 task_obj
                    self.reg_gm_task(task_name, task_obj)
                    # 将 worker 名放入列表 用来检查worker名冲突
                    self.task_list[task_name] = plugin
                    print ' '.join([plugin, '-->', task_name])

            # 单独注册监控用的task
            self.reg_gm_task('monitor_{}_ok'.format(self.worker_name), monitor_worker_ok)

    def run(self):
        """走你.
        """
        try:
            self._boring()
            self.gm_wk = gearman.GearmanWorker(self.gm_host_list)
            self.gm_wk.set_client_id(self.clinent_id)
            self._load_plugin()
            self.gm_wk.work()
        except KeyboardInterrupt:
            print('\rShutdown ...')
            self.gm_wk.shutdown()
            print('Bye ~')
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e

    def _boring(self):
        f = Figlet(width=150)
        font_lst = [
            "s-relief", "georgia11", "varsity", "univers", "train", "marquee",
            "tiles", "ticksslant", "ticks", "sweet", "swampland", "3d_diagonal",
            "sub-zero", "stellar", "starwars", "smpoison", "rozzo", "invita",
            "roman", "rev", "rectangles", "poison", "alligator", "3-d", "block",
            "peaksslant", "peaks", "p_skateb", "os2", "nscript", "georgia11",
            "o8", "nipples", "nancyj-fancy", "modular", "merlin1", "flowerpower",
            "lildevil", "letters", "lean", "larry3d", "kban", "fraktur", "defleppard",
            "dancingfont", "crazy", "cosmic", "contrast", "chunky", "chiseled",
            "catwalk", "caligraphy", "broadway", "bright", "blocks", "dotmatrix",
            "bigchief", "bear", "banner3", "banner3-D", "banner", "acrobatic"
        ]
        font = random.choice(font_lst)
        f.setFont(font=font)
        print(f.renderText('WEHOME'))
