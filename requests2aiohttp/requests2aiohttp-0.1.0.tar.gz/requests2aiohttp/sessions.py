import aiohttp
import asyncio


_sentinel = object()


class Session:
    """
    This class needs to be inserted just before the class you intend to inherit
    """

    def __init__(self, connector=None, **kwargs):
        self.session = aiohttp.ClientSession(connector=connector)
        super().__init__(**kwargs)

    def get(self, url, stream=None, timeout=_sentinel, params=_sentinel,
            **unknown_kwargs):
        if unknown_kwargs:
            raise NotImplementedError(
                "Not implemented requests' keyword arguments: %s"
                % ", ".join(unknown_kwargs.keys()))
        aiohttp_kwargs = {}
        if timeout is not _sentinel:
            aiohttp_kwargs['timeout'] = timeout
        if params is not _sentinel:
            aiohttp_kwargs['params'] = self._clean_params(params)
        return Response(self.session.get(url, **aiohttp_kwargs))

    async def close(self):
        print("### close session")
        await self.session.close()
        super().close()

    def _render_param(self, param):
        if isinstance(param, bool):
            return ("true" if param else "false")
        elif isinstance(param, (str, int)):
            return param
        else:
            raise NotImplementedError(
                "Unknown param type %r: %r", type(param), param)

    def _clean_params(self, params):
        if params is None:
            return None
        else:
            return {
                k: self._render_param(v)
                for k, v in params.items()
                if v is not None
            }


class Response:
    """
    _RequestContextManager wrapper for requests.Response compatibility
    """
    def __init__(self, context):
        self.context = context
        self.will_raise_for_status = False

    def raise_for_status(self):
        self.will_raise_for_status = True

    async def _json(self):
        async with self.context as resp:
            if self.will_raise_for_status:
                resp.raise_for_status()
            return await resp.json()

    def json(self):
        return asyncio.ensure_future(self._json())

    async def _content(self):
        async with self.context as resp:
            if self.will_raise_for_status:
                resp.raise_for_status()
            return await resp.read()

    @property
    def content(self):
        return self._content()

    @property
    def raw(self):
        return self.context
