
class AsyncContextManager:
    def __init__(self, f):
        self.f = f
    
    def __call__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        return self

    async def __aenter__(self):
        self.it = self.f(*self.args, **self.kwargs).__aiter__()
        v = await self.it.__anext__()
        return v

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self.it.__anext__()
        except StopAsyncIteration: pass


