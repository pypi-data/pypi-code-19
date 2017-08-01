
import logging
import asyncio
import mugen

logging.basicConfig(level=logging.DEBUG)


headers = {
'Connection': 'keep-alive',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, sdch',
}


async def task1():
    # resp = await mugen.get('https://httpbin.org/headers', proxy='http://115.226.11.3:9992')
    resp = await mugen.get('https://www.zybang.com/question/a1d38f335ffa88d0ccb14907885db6b1.html', proxy='http://115.226.11.3:9992')
    # resp = await mugen.post('https://httpbin.org/post', data={'a':1, 'b': 2}, proxy='http://115.226.11.3:9992')
    print(list(resp.headers.items()))
    print(resp.text)
    print(len(resp.text))


loop = asyncio.get_event_loop()
tasks = asyncio.wait([task1()])
loop.run_until_complete(tasks)

