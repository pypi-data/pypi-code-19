#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template
import json
import os.path
import time
import htmlmin

class Resource:
    __STYLE_HOOK = u'<!--[FIS_STYLE_HOOK]-->'
    __SCRIPT_HOOK = u'<!--[FIS_SCRIPT_HOOK]-->'
    __FRAMEWORK_HOOK = u'<!--[FIS_FRAMEWORK_HOOK]-->'
    __RESOURCE_MAP_HOOK = u'<!--[FIS_RESOURCE_MAP_HOOK]-->'
    __framework_res_id = None
    __res_map = {}
    __style_list = []
    __script_list = []
    __lib_script_list = []
    __inline_style_list = []
    __inline_script_list = []
    __async_list = []
    __context = {}
    __static_folder = ''
    __template_folder = ''
    __debug = False
    __cache_time = 60 * 60
    __now = None

    def __init__(self):
        pass

    @classmethod
    def set_config(cls, static_folder, template_folder, debug=False, cache_time=None):
        cls.__static_folder = static_folder
        cls.__template_folder = template_folder
        cls.__debug = debug
        cls.__cache_time = cache_time
        cls.__now = time.time()

    @classmethod
    def __set_res_map(cls, namespace):
        path = os.path.join(os.path.abspath(cls.__static_folder), namespace if namespace else '', 'map.json')
        if not os.path.isfile(path):
            raise 'MAP文件不存在'
        try:
            with open(path, 'r') as f:
                if namespace:
                    cls.__res_map[namespace] = json.load(f)
                else:
                    cls.__res_map = json.load(f)
        except:
            raise 'MAP文件读取异常'

    @classmethod
    def load(cls, res_id):
        cls.__load(res_id)

    @classmethod
    def get_uri(cls, res_id):
        return cls.__get_uri(res_id)

    @classmethod
    def __get_template_real_name(cls, res_id):
        result = cls.__parse_res_id(res_id)
        return result[0] + '/' + result[1] if result[0] else result[1]

    @classmethod
    def __get_namespace_from_res_id(cls, res_id):
        result = cls.__parse_res_id(res_id)
        return result[0]

    @classmethod
    def __parse_res_id(cls, res_id):
        result = res_id.split(':', 1)
        namespace = None
        if len(result) == 2:
            namespace = result[0]
        return [namespace, result[-1]]

    @classmethod
    def render_template(cls, res_id, **context):
        cls.__reset(**context)
        output_html = cls.__render_flask_template(cls.__get_template_real_name(res_id))
        cls.__load(res_id)
        output_html = cls.__output_style(output_html)
        output_html = cls.__output_framework(output_html)
        output_html = cls.__output_resource_map(output_html)
        output_html = cls.__output_script(output_html)
        if not cls.__debug:
            output_html = htmlmin.minify(output_html)
        return output_html

    @classmethod
    def __render_flask_template(cls, template_name_or_list):
        return render_template(template_name_or_list, **cls.__context)

    @classmethod
    def __reset(cls, **context):
        del cls.__style_list[:]
        del cls.__inline_style_list[:]
        del cls.__lib_script_list[:]
        del cls.__script_list[:]
        del cls.__inline_script_list[:]
        del cls.__async_list[:]
        cls.__context = context

    @classmethod
    def __load_deps(cls, res_id):
        res = cls.__get_res_or_pkg_info(res_id)
        deps = res.get('deps')
        if not deps:
            return
        for dep in deps:
            cls.__load(dep)

    @classmethod
    def __load(cls, res_id):
        res = cls.__get_res_or_pkg_info(res_id)
        if not res:
            return
        cls.__load_deps(res_id)
        cls.__load_async(res_id)
        # fis3默认打包
        if res.get('pkg'):
            cls.__load(res.get('pkg'))
            return
        # fis3-postpackager-loader
        if res.get('aioPkg'):
            if not cls._is_page_res(res_id):  # 非"页面级打包资源"不加载
                return
            cls.__load(res.get('aioPkg'))
            return
        cls.__add_res(res_id)

    @classmethod
    def _is_page_res(cls, res_id):
        namespace = cls.__get_namespace_from_res_id(res_id)
        start = 'page' if not namespace else namespace + ":" + 'page'
        return res_id.startswith(start)

    @classmethod
    def __add_css(cls, res_id):
        if res_id not in cls.__style_list:
            cls.__style_list.append(res_id)

    @classmethod
    def __add_js(cls, res_id):
        if res_id not in cls.__script_list:
            cls.__script_list.append(res_id)

    @classmethod
    def __output_style(cls, html):
        _list = []
        for res_id in cls.__style_list:
            _list.append(cls.__get_link_html(res_id))
        for style in cls.__inline_style_list:
            _list.append(style)
        _list = u'\n'.join(_list)
        return unicode(html).replace(cls.__STYLE_HOOK, _list)

    @classmethod
    def __output_script(cls, html):
        _list = []
        for res_id in cls.__script_list:
            _list.append(cls.__get_script_html(res_id))

        for script in cls.__inline_script_list:
            _list.append(script)
        _list = u'\n'.join(_list)
        return unicode(html).replace(cls.__SCRIPT_HOOK, _list)

    @classmethod
    def __output_framework(cls, html):
        if cls.__framework_res_id is None:
            return html
        return unicode(html).replace(cls.__FRAMEWORK_HOOK, cls.__get_script_html(cls.__framework_res_id))

    @classmethod
    def __output_resource_map(cls, html):
        return unicode(html).replace(cls.__RESOURCE_MAP_HOOK, cls.__get_resource_map_html())

    @classmethod
    def __get_resource_map_html(cls):
        if not cls.__get_resource_map():
            return u''
        return u'<script type="text/javascript">require.resourceMap(' + json.dumps(cls.__get_resource_map()) + u')</script>'

    @classmethod
    def placeholder(cls, hook_type):
        if hook_type == 'css':
            return cls.__STYLE_HOOK
        if hook_type == 'js':
            return cls.__SCRIPT_HOOK
        if hook_type == 'framework':
            return cls.__FRAMEWORK_HOOK
        if hook_type == 'resource_map':
            return cls.__RESOURCE_MAP_HOOK
        return ''

    @classmethod
    def framework(cls, res_id):
        cls.__framework_res_id = res_id
        return ''

    @classmethod
    def __get_link_html(cls, res_id):
        return cls.__get_link_html_by_source(cls.__get_uri(res_id))

    @classmethod
    def __get_link_html_by_source(cls, source):
        if source:
            return u'<link rel="stylesheet" type="text/css" href="' + source + u'"/>'
        return

    @classmethod
    def __get_script_html(cls, res_id):
        return cls.__get_script_html_by_source(cls.__get_uri(res_id))

    @classmethod
    def __get_script_html_by_source(cls, source):
        if source:
            return u'<script type="text/javascript" src="' + source + u'"></script>'
        return

    @classmethod
    def __get_res_info(cls, res_id):
        res_map = cls.__get_res_map_from_res_id(res_id)
        res = res_map.get('res')
        return res.get(res_id)

    @classmethod
    def __get_pkg_info(cls, res_id):
        res_map = cls.__get_res_map_from_res_id(res_id)
        pkg = res_map.get('pkg')

        return pkg.get(res_id)

    @classmethod
    def __get_uri(cls, res_id):
        res = cls.__get_res_or_pkg_info(res_id)
        return res.get('uri')

    @classmethod
    def __get_id(cls, res_id):
        res = cls.__get_res_info(res_id)
        extras = res.get('extras')
        if not extras:
            return res_id
        id = extras.get('moduleId')
        if not id:
            return res_id
        return id

    @classmethod
    def style(cls, content):
        cls.__inline_style_list.append(content)

    @classmethod
    def script(cls, content):
        cls.__inline_script_list.append(content)

    @classmethod
    def __get_res_or_pkg_info(cls, res_id):
        res = cls.__get_res_info(res_id)
        pkg = cls.__get_pkg_info(res_id)
        return res if res else pkg

    @classmethod
    def __add_res(cls, res_id):
        res = cls.__get_res_or_pkg_info(res_id)
        if not res:
            return
        if cls.__is_css(res_id, res):
            cls.__add_css(res_id)
            return
        if cls.__is_js(res_id, res):
            cls.__add_js(res_id)

    @classmethod
    def __get_resource_map(cls):
        if not cls.__async_list:
            return None
        __resource_map = {
            'res': {},
            'pkg': {}
        }
        for async in cls.__async_list:
            __resource_map['res'][cls.__get_id(async)] = {
                'url': cls.__get_uri(async)
            }

        return __resource_map

    @classmethod
    def __load_async(cls, res_id):
        res = cls.__get_res_info(res_id)
        if not res:
            return
        extras = res.get('extras')
        if not extras:
            return
        asyncs = extras.get('async')
        if not asyncs:
            return
        for async in asyncs:
            cls.__add_async_res(async)

    @classmethod
    def __add_async_res(cls, async):
        if async in cls.__style_list:
            return
        if async in cls.__script_list:
            return
        if async not in cls.__async_list:
            cls.__async_list.append(async)

    @classmethod
    def __get_res_map_from_res_id(cls, res_id):
        namespace = cls.__get_namespace_from_res_id(res_id)
        cls.__update_res_map(namespace)
        if not namespace and cls.__res_map:
            return cls.__res_map
        if namespace and cls.__res_map.get(namespace):
            return cls.__res_map.get(namespace)

        return cls.__res_map if not namespace else cls.__res_map.get(namespace)

    @classmethod
    def __update_res_map(cls, namespace):
        if cls.__debug:
            cls.__set_res_map(namespace)
            return
        now = time.time()
        if cls.__cache_time and (now - cls.__now) > cls.__cache_time:
            cls.__set_res_map(namespace)
            cls.__now = now
            return
        if not namespace and cls.__res_map:
            return
        if namespace and cls.__res_map.get(namespace):
            return
        cls.__set_res_map(namespace)

    @classmethod
    def __is_js(cls, res_id, res=None):
        if res_id.endswith('.js'):
            return True
        if res and res.get('type') == 'js':
            return True
        return False

    @classmethod
    def __is_css(cls, res_id, res=None):
        if res_id.endswith('.css'):
            return True
        if res and res.get('type') == 'css':
            return True
        return False
