# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
import sys

from .base import BaseMiddleware
from ...utils import update_wrapper


class FlaskMiddleware(BaseMiddleware):

    def __call__(self, original):

        def wrapped(*args, **kwargs):
            """ Call the lifecycles methods with these arguments:
            Pyramid pre callbacks will receive these arguments:
            (None)
            Flask post callbacks will receive these arguments:
            (None, response)
            Flask failing callbacks will receive these arguments:
            (None, exception)
            """
            self.strategy.before_hook_point()
            self.execute_pre_callbacks(record_500=True)

            try:
                response = original(*args, **kwargs)
            except Exception:
                self.execute_failing_callbacks(sys.exc_info())
                raise

            return self.execute_post_callbacks(response, record_500=True)

        update_wrapper(wrapped, original)

        return wrapped
