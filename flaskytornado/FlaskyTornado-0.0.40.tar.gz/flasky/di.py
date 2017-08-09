import inspect

from flasky import errors


SINGLETON = 0
PROTOTYPE = 1

#: TODO: implement forbidden object names filter to avoid
#:       conflict with tornado's handler properties.


def _raise_configuration_err(message=None, context=None):
    raise errors.FError(
        err_msg=message,
        err_code='errors.internalErrors',
        status_code=500,
        context=context
    )


class DIContainer(object):

    def __init__(self, app):
        self._app = app
        self.init_app(app)
        self._registered_names = set()
        self._factory_funcs = {}
        self._instance_registry = {}
        self._objects_currently_in_creation = set()

    @property
    def registered_object_count(self):
        return len(self._factory_funcs)

    @property
    def object_count(self):
        return len(self._instance_registry)

    async def before_request_hook(self, handler, method_definition):
        setattr(handler, "di", self)

    async def on_start_hook(self, app):
        for registered_name in self._registered_names:
            instance = await self.get(registered_name)
            if instance is None:
                _raise_configuration_err(message="Registerd function<{}> returned None".format(registered_name),)

    def __getattr__(self, attr):
        if attr not in self._instance_registry:
            _raise_configuration_err(message=
                    "Object is not found with name<{}> in registery"
                    .format(attr))
        return self._instance_registry[attr]

    def init_app(self, app):
        app.before_request(self.before_request_hook)
        app.on_start(self.on_start_hook)

    def register(self, name=None, strategy=SINGLETON):
        def decorator(f):
            register_name = name or self._resolve_name(f)
            dependency_names = self._resolve_dependencies_name(f)

            self._factory_funcs[register_name] = {
                "factory_func": f,
                "strategy": strategy,
                "dependencies": dependency_names
            }

            self._registered_names.add(register_name)
            return f

        return decorator

    def _resolve_name(self, f):
        return f.__name__

    def _resolve_dependencies_name(self, f):
        return list(inspect.signature(f).parameters.keys())

    async def get(self, name):
        if name in self._instance_registry:
            return self._instance_registry[name]

        return await self.create(name)

    async def resolve_dependencies(self, dependency_names, **kwargs):
        dependency_names = dependency_names or []
        params = []
        for parameter in dependency_names:
            if parameter in kwargs:
                params.append(kwargs[parameter])
            else:
                params.append(await self.get(parameter))

        return params

    async def create(self, name):
        if name not in self._factory_funcs:
            _raise_configuration_err(message=
                    'Dependent object<{}> not found.'.format(name))

        if name in self._objects_currently_in_creation:
            reference = "->".join(list(self._objects_currently_in_creation))
            _raise_configuration_err(message=
                    'Circular Reference detected. {}'.format(reference))

        self._objects_currently_in_creation.add(name)

        factory_func_def = self._factory_funcs[name]

        params = await self.resolve_dependencies(factory_func_def.get('dependencies'))

        instance = await factory_func_def["factory_func"](*params)
        #: Cache instance if its strategy is singleton
        if factory_func_def["strategy"] == SINGLETON:
            self._instance_registry[name] = instance

        self._objects_currently_in_creation.remove(name)

        return instance

    async def inject_and_run(self, f, **kwargs):
        parameter_names = self._resolve_dependencies_name(f)
        params = await self.resolve_dependencies(parameter_names, **kwargs)

        if inspect.iscoroutinefunction(f):
            return await f(*params)
        else:
            return f(*params)


