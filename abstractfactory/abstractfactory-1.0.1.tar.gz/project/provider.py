class Provider():
    def get_kwarg(self, name, **kwargs):
        if name in kwargs:
            return kwargs[name]
        return ''

    def get_arg(self, name, *args):
        if len(args) > 0:
            return args[0]
        return ''

    def execute(self, required_parameter, *args):
        raise NotImplementedError('execute is not implemented')