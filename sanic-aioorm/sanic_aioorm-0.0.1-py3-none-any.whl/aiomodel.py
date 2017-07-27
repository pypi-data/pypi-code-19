__all__ = ["Model"]
from aioorm import AioModel
from aioorm import model_to_dict


class ToDictMixin:
    async def to_dict(self, **kws):
        result = await model_to_dict(self, **kws)
        return result


class Model(AioModel, ToDictMixin):
    pass
