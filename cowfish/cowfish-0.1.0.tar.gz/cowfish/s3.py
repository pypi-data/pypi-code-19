import asyncio
import aiohttp
import aiobotocore
from urllib import parse


class S3ClientPool:
    def __init__(self, region_name, size):
        self.session = aiobotocore.get_session()
        self.size = size
        self.semaphore = asyncio.Semaphore(size)
        self.clients = [
            self.session.create_client('s3', region_name=region_name)
            for i in range(size)
        ]

    async def acquire(self):
        await self.semaphore.acquire()
        return self.clients.pop(0)

    def recycle(self, client):
        self.clients.append(client)
        self.semaphore.release()

    def release(self):
        for client in self.clients:
            client.close()


class S3Uploader:
    def __init__(self, bucket, region_name, prefix=None, concurrency=3):
        self.bucket = bucket
        self.region_name = region_name
        self.prefix = prefix
        self.concurrency = concurrency
        self.pool = S3ClientPool(region_name, concurrency)

    async def s3_upload(self, info):
        session = aiohttp.ClientSession()
        async with session:
            async with session.get(info['url']) as response:
                body = await response.read()
        client = await self.pool.acquire()
        try:
            suffix = parse.urlparse(info['url']).path.split('.')[-1]
            if suffix not in ['jpg', 'png', 'jpeg']:
                suffix = 'jpg'
            key = info['hash'] + '.' + suffix
            if self.prefix is not None:
                key = self.prefix + '/' + key
            print('upload image from {} to {} {}'.format(
                info['url'], key, response.content_type))
            resp = await client.put_object(Bucket=self.bucket,
                                           Key=key,
                                           Body=body,
                                           ContentType=response.content_type)
            print(resp)
        finally:
            self.pool.recycle(client)

    def upload_all(self, infos):
        loop = asyncio.get_event_loop()
        coro = batch_ops(infos, self.concurrency, self.s3_upload)
        loop.run_until_complete(coro)

    def __del__(self):
        self.pool.release()


async def batch_ops(obj_list, concurrency, coro_func, timeout=None):
    obj_iter = iter(obj_list)
    result = []
    pending = []
    while True:
        try:
            obj = next(obj_iter)
        except StopIteration:
            pass
        else:
            job = coro_func(obj)
            pending.append(job)
            if len(pending) < concurrency:
                continue
        if not pending:
            break
        done, pending_set = await asyncio.wait(
            pending, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        pending = list(pending_set)
        result.append(done.pop())
    return result


def main():
    s3_uploader = S3Uploader('test-gyb', 'us-west-1')
    s3_uploader.upload_all([
        'http://i.imgur.com/l0sYs8S.jpg',
        'http://i.imgur.com/hBuSQA5.png',
        'http://i.imgur.com/Z65buhC.jpg',
        'http://i.imgur.com/wGlA8A4.jpg',
    ])


if __name__ == '__main__':
    main()
