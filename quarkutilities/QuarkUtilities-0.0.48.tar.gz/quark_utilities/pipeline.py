import inspect

from flasky import errors


class FPipelineContext(object):

    def __init__(self):
        pass

    def create(self, f_list):
        return FPipeline(f_list, self.di, parent_ctx=self)



class FPipeline(object):

    def __init__(self, f_list, di):
        self.f_list = f_list
        self.di = di

    async def run(self, data, **kwargs):

        for f in self.f_list:
            func_args = list(inspect.signature(f).parameters.keys())
            parameters = self._resolve_parameters(func_args)

    async def _resolve_parameters(self, func_args):
        for func_arg in func_args:
            try:
                parameter = await self.di.get(func_arg)
            except errors.ConfigurationError:
                raise errors.FError(
                    err_msg='Function argument is not found in DI '
                )



