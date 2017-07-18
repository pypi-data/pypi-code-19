import sys
from datetime import datetime
import asyncio

from . import sound, utils


async def count_down(duration):
    global running
    while running:
        await asyncio.sleep(1)
        duration -= 1
        msg = 'Remaining' if duration > 0 else 'OVER TIME'
        print('\r{}: {}'.format(
            msg,
            utils.format_time_interval(duration)),
            end='',
            flush=True)


def start_interval(duration, actions, soundfile):
    global running
    running = True
    t0 = datetime.now()

    player = sound.SoundPlayer(soundfile)

    loop = asyncio.get_event_loop()
    loop.call_later(duration, player.play)
    loop.call_later(duration, player.schedule, duration, loop)
    futures = [count_down(duration), manage_input(loop, actions)]

    loop.run_until_complete(asyncio.wait(futures))

    t1 = datetime.now()

    return t1 - t0


class Prompt:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.q = asyncio.Queue(loop=self.loop)
        self.loop.add_reader(sys.stdin, self.got_input)

    def got_input(self):
        asyncio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self, msg, end='\n', flush=False):
        print(msg, end=end, flush=flush)
        return (await self.q.get()).rstrip('\n')


async def manage_input(loop, actions):
    global running
    description = '\n' + '\n'.join(['{} -> {}'.format(key, value[0])
                                    for key, value in actions.items()]) + '\n'
    prompt = Prompt(loop)
    while running:
        key = await prompt(description)
        if key in actions:
            running = actions[key][1]()
