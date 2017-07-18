#coding: utf8
"""
Autodoc
-------------
Данный модуль позволяет в автоматическом режиме документировать методы Flask API.

Принцип работы:

* При прогоне тестов, если установлена переменная окружения AUTODOC_WRITE при вызове декорированной
  декоратором :func:`.autodoc_dec` функции, результат ее выполнения и параметры запроса сохраняются
  в файл .calls.

* В docstring функции нужно указать параметр <examples>. Он будет заменен на
  примеры запросов к функции.

Пример::

    @app.route(...)
    @autodoc_dec()
    def some_route():
        '''
        Примеры запросов:

        <examples>

        '''
        ...


.. note::

    Для сохранения вызовов нужно указать переменную окружения AUTODOC_WRITE.

"""
import contextlib
import threading
from functools import wraps

from autodocumentation.doc_builder import DocBuilder
from autodocumentation.flask_writer import FlaskRequestWriter

_locals = threading.local()

class autodoc(object):

    def __init__(self, writer=FlaskRequestWriter(), doc_builder=DocBuilder()):
        self.doc_builder = doc_builder
        self.writer = writer
        self.doc_builder.writer = self.writer

    @classmethod
    @contextlib.contextmanager
    def context(cls, **k):
        try:
            _locals.context = k
            yield
        finally:
            del _locals.context

    @classmethod
    def get_context(cls):
        return getattr(_locals, "context", {})

    @classmethod
    def set_key(cls, key):

        def dec(func):
            func.__autodoc_key__ = key
            return func

        return dec

    def decorator(self, func):
        @wraps(func)
        def inner(*a, **k):

            output = func(*a, **k)

            if self.writer.allow_write():
                self.writer.write(
                    func, output, *a, **k
                )

            return output

        self.doc_builder.add_doc(inner)

        return inner