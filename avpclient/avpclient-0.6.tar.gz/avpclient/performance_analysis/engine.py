import asyncio
import logging
import time

import aiohttp

from avpclient import constants as const

# setting up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)
MAX_CONNECTION = 1000


# asyncio http consumer
async def consumer(main_queue, dlq, session, responses):
    while True:
        try:
            # Fetch the url from the queue, blocking until the queue has item
            request = await main_queue.get()
            # Try to get a response from the sever

            ts = time.time()
            async with session.post(url=const.base_url + request['url'], json=request['data'].to_json(),
                                    params=request['parameters']) as response:
                # Check we got a valid response
                response.raise_for_status()
                # append it to the responses lists
                responses.append(await response.json())
                # telling the queue we finished processing the massage
                main_queue.task_done()

            te = time.time()

            logger.debug("Total time take for request: (%s). Number of items remain: Main_queue: (%s), DLQ: (%s)",
                         str(te - ts), str(main_queue.qsize()), str(dlq.qsize()))

        # In case of a time in our get request/ problem with response code
        except asyncio.TimeoutError:
            logger.debug("Timeout error with request to %s, Moving to DLQ. -(%s). main_queue: (%s), dlq: (%s)" %
                         (request['url'], " ".join(request['data'].columns), str(main_queue.qsize()), str(dlq.qsize())))
            # we put the url in the dlq, so other consumers wil handle it
            await dlq.put(request)
            # lower the pace
            asyncio.sleep(0.1)
            # telling the queue we finished processing the massage
            main_queue.task_done()
        except aiohttp.ClientError as client_error:
            logger.debug("Server processing problem with request to %s, Moving to DLQ. - (%s). main_queue: (%s), dlq: (%s)" %
                         (request['url'], " ".join(request['data'].columns), str(main_queue.qsize()), str(dlq.qsize())))
            # we put the url in the dlq, so other consumers wil handle it
            await dlq.put(request)
            # lower the pace
            asyncio.sleep(0.1)
            # telling the queue we finished processing the massage
            main_queue.task_done()

async def produce(queue, itr_items):
    for item in itr_items:
        # if the queue is full(reached maxsize) this line will be blocked
        # until a consumer will finish processing a url
        await queue.put(itr_items[item])

async def process_last_n_requests(session, consumer_num, requests):
    # We init the main_queue with a fixed size, and the dlq with unlimited size
    main_queue, dlq, responses = asyncio.Queue(maxsize=2000), asyncio.Queue(), []

    # we init the consumers, as the queues are empty at first,
    # they will be blocked on the main_queue.get()
    consumers = [asyncio.ensure_future(
        consumer(main_queue, dlq, session, responses))
        for _ in range(consumer_num)]
    # init the dlq consumers, same as the base consumers,
    # Only main_queue is the dlq.
    dlq_consumers = [asyncio.ensure_future(
        consumer(main_queue=dlq, dlq=dlq, session=session, responses=responses))
        for _ in range(10)]

    producer = await produce(queue=main_queue, itr_items=requests)

    # wait for all item's inside the main_queue to get task_done
    await main_queue.join()


    # wait for all item's inside the dlq to get task_done
    await dlq.join()

    # cancel all co-routines
    for consumer_future in consumers + dlq_consumers:
        consumer_future.cancel()

    return responses


async def run(loop, n, requests):
    conn_num = min(MAX_CONNECTION, n)

    try:
        # we init more connectors to get better performance
        async with aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(limit_per_host=conn_num, verify_ssl=False),
                   headers=const.api_key_header
        ) as session:
            result = await process_last_n_requests(session, conn_num, requests)

            return result
    except Exception as e:
        print(repr(e))
