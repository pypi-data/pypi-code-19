from collections import ChainMap
import functools
import contextlib


class SafeContextManager(contextlib._GeneratorContextManager):
    def __exit__(self, type, value, traceback):
        try:
            next(self.gen)
        except StopIteration:
            if type is None:
                return
        else:
            if type is None:
                raise RuntimeError("generator didn't stop")
        return super().__exit__(type, value, traceback)


def safe_contextmanager(func):
    """absolutely call next(), contextmanager()"""

    @functools.wraps(func)
    def helper(*args, **kwds):
        return SafeContextManager(func, args, kwds)

    return helper


class Context:
    def __init__(self, args=None, kwargs=None):
        self.args = args or []
        self.kwargs = kwargs or {}

    def __repr__(self):
        return "<ctx args={!r}, kwargs={!r}>".format(self.args, self.kwargs)

    def merge(self, value):
        if value is None:
            return self
        elif hasattr(value, "keys"):
            return self.__class__(self.args, ChainMap(value, self.kwargs))
        elif isinstance(value, (list, tuple)):
            return self.__class__([*self.args, *value], ChainMap({}, self.kwargs))
        else:
            args = self.args[:]
            args.append(value)
            return self.__class__(args, ChainMap({}, self.kwargs))

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.args[i]
        else:
            return self.kwargs[i]

    def __setitem__(self, i, v):
        if isinstance(i, int):
            self.args[i] = v
        else:
            self.kwargs[i] = v

    def get(self, i, default=None):
        return self.kwargs.get(i, default)


def with_context(fn):
    fn._with_context = True
    return fn


def need_context(fn):
    return hasattr(fn, "_with_context")


class FixtureManager:
    def __init__(self):
        self.fixtures = []
        self.registered = {}

    def yield_fixture(self, fixture):
        lifted = self.lift(fixture)
        self.fixtures.append(lifted)
        self.registered[fixture] = lifted
        return fixture

    def lift(self, fixture):
        return safe_contextmanager(fixture)

    def get_or_self(self, f):
        return self.registered[f] if f in self.registered else f


def dispatch_default(f, ctx):
    args = []
    if need_context(f):
        args.append(ctx)
    return f(*args)


class App:
    def __init__(self, dispatcher=None, manager=None):
        self.dispatcher = dispatcher or dispatch_default
        self.manager = manager or FixtureManager()

    def yield_fixture(self, fixture):
        return self.manager.yield_fixture(fixture)

    @property
    def fixtures(self):
        return self.manager.fixtures

    @contextlib.contextmanager
    def run_fixture(self, fixtures=None, context=None):
        fixtures = [self.manager.get_or_self(f) for f in (fixtures or self.fixtures)]
        ctx = context or Context()  # todo: scope
        with self._run_fixture(ctx, fixtures) as ctx:
            yield ctx

    @contextlib.contextmanager
    def _run_fixture(self, ctx, fixtures):
        if not fixtures:
            yield ctx
        else:
            with self.dispatcher(fixtures[0], ctx) as val:
                with self._run_fixture(ctx.merge(val), fixtures[1:]) as ctx:
                    yield ctx

    def run(self, args):
        if callable(args):
            fn = args
            fixtures = None
            with self.run_fixture(fixtures) as ctx:
                return fn(*ctx.args, **ctx.kwargs)
        else:
            fixtures = args

            def _run(fn):
                with self.run_fixture(fixtures) as ctx:
                    return fn(*ctx.args, **ctx.kwargs)

            return _run

    __call__ = run


def create(*, dispatcher=None, manager=None):
    runner = App(dispatcher, manager)
    return runner, runner.yield_fixture
