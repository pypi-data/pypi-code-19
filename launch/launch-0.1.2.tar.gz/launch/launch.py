# coding=utf-8
# Copyright 2017 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import importlib
import os

import yaml
from flowdas import meta

from .version import __version__

__all__ = [
    'LaunchNotFoundError',
    'ConfigurationError',
    'Launch',
    'define',
]


class LaunchNotFoundError(Exception):
    """launch.yaml 파일을 발견할 수 없을 때 발생하는 예외.

    Since version 0.1.
    """
    pass


class ConfigurationError(Exception):
    """launch.yaml 이 문법에 맞지 않을 때 발생하는 예외.

    Attributes:
        location (str):
            오류의 위치가 JSON Pointer 형식으로 제공된다.
        value (str):
            오류를 일으킨 값.

    Since version 0.1.
    """

    def __init__(self, context):
        if isinstance(context, meta.Context):
            self.location = context.errors[0].location
            self.value = context.errors[0].value
        else:
            self.location = context['location']
            self.value = context['value']


_defines = {}


def define(name, prop=None):
    """launch.yaml 의 정의를 확장한다.

    name 은 최상단 파라미터의 이름.

    prop 는 파라미터의 형을 지정하는 :py:class:`flowdas.meta.Property` 인스턴스. 생략하면 :py:class:`flowdas.meta.String` ().

    이미 정의되어 있다면 오버라이드 한다.

    Since version 0.1.
    """
    if prop is None:
        prop = meta.String()
    _defines[name] = prop


class Launch(object):
    """launch.yaml 파일로 정의되는 환경.

    :param root: 설정 파일이 들어있는 디렉토리 경로.

    Since version 0.1.
    """

    class Config(meta.Entity):
        """"""
        plugins = meta.String[:](required=True)

    _instances = {}
    _current = None

    __slots__ = ('_root', '_config')

    def __new__(cls, root):
        root = Launch._norm_root(root)
        instance = Launch._instances.get(root)
        if instance is None:
            instance = super(Launch, cls).__new__(cls)
            Launch._instances[root] = instance
        return instance

    def __init__(self, root):
        if hasattr(self, '_root'):
            return
        self._root = Launch._norm_root(root)
        if not os.path.exists(os.path.join(self._root, self.launch_file())):
            raise LaunchNotFoundError()
        try:
            with open(os.path.join(self._root, self.launch_file()), 'rb') as f:
                data = yaml.safe_load(f) or {}
            #
            # two-phase configuration loading
            #

            # first phase
            # 기본 설정만 로딩한 후 플러그인들을 임포트한다.
            Launch._current = self
            try:
                for modname in self.builtins():
                    importlib.import_module(modname)
            finally:
                Launch._current = None
            context = meta.Context()
            try:
                self._config = self.Config().load(data, context)
                self._config.validate()
            except ValueError:
                raise ConfigurationError(context)
            assert Launch._current is None
            Launch._current = self
            try:
                for modname in (self._config.plugins or []):
                    importlib.import_module(modname)
            finally:
                Launch._current = None

            # second phase
            # 플로그인들의 설정을 반영해서 최종 로딩한다.
            CustomConfig = self.Config.define_subclass('Config', _defines)
            context = meta.Context()
            try:
                self._config = CustomConfig().load(data, context)
                self._config.validate()
            except ValueError:
                raise ConfigurationError(context)
        except:
            del Launch._instances[self._root]
            raise

    @staticmethod
    def _norm_root(root):
        root = os.path.abspath(os.path.expanduser(root))
        return root

    @property
    def root(self):
        """설정 파일이 들어있는 디렉토리 경로.

        Since version 0.1.
        """
        return self._root

    @property
    def config(self):
        """설정이 저장되는 객체.

        Since version 0.1.
        """
        return self._config

    @classmethod
    def launch_file(cls):
        """설정 파일의 이름.

        Since version 0.1.
        """
        return 'launch.yaml'

    @classmethod
    def builtins(cls):
        """내장 패키지들의 목록.

        Since version 0.1.
        """
        return []

    @classmethod
    def version(cls):
        """버전 문자열.

        Since version 0.1.
        """
        return __version__
