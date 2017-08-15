from tornado.platform.asyncio import to_asyncio_future
from tornado.stack_context import StackContextInconsistentError, _state

#: This implementation is based on
#: https://gist.github.com/virtuald/50bf7cacdc8cfb05e323f350539f0efa
from flasky import errors

CURRENT_APP = None

def set_current_app(app):
    global CURRENT_APP

    if CURRENT_APP:
        raise errors.FError(
            err_code='errors.internalError',
            err_msg='Application is already set. Please check your bootstraping logic',
            status_code=500
        )

    CURRENT_APP = app


class BaseContext(object):

    def __init__(self, data=None):
        if data is None:
            data = {}

        self.active = True
        self.data = data

    def enter(self):
        pass

    def exit(self, type, value, traceback):
        pass

    def __enter__(self):
        self.old_contexts = _state.contexts
        self.new_contexts = (self.old_contexts[0] + (self,), self)
        _state.contexts = self.new_contexts

        return self

    def __exit__(self, type, value, traceback):
        final_contexts = _state.contexts
        _state.contexts = self.old_contexts

        if final_contexts is not self.new_contexts:
            raise StackContextInconsistentError(
                'stack_context inconsistency (may be caused by yield '
                'within a "with StackContext" block)')

        self.new_contexts = None

    def deactivate(self):
        self.active = False

    @classmethod
    def current(cls):
        for ctx in reversed(_state.contexts[0]):
            if isinstance(ctx, cls) and ctx.active:
                return ctx

    @classmethod
    def current_app(cls):
        return CURRENT_APP

    @classmethod
    def current_data(cls):
        for ctx in reversed(_state.contexts[0]):
            if isinstance(ctx, cls) and ctx.active:
                return ctx.data

    @classmethod
    def get_param(cls, key):
        return cls.current_data().get(key, None)

    def prev_ctx(self):
        '''
            Walks up the list of contexts to find another one of this type

            .. note:: The 'top' of the context stack is where a NullContext
                      was used, so this cannot walk past a NullContext
        '''
        cls = self.__class__
        for ctx in reversed(self.old_contexts[0]):
            if isinstance(ctx, cls) and ctx.active:
                return ctx

def run_with_stack_context(context, func):
    with context:
        return to_asyncio_future(func())