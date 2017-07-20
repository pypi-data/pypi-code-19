class CallbackBase(object):

    def __init__(self, sounds):
        self.sounds = sounds
        self.in_progress = {}

    def _call(self, func, pkt):
        func_name = str(func)
        cb = self.in_progress.get(func_name)
        if cb:
            try:
                cb.send(pkt)
            except StopIteration:
                    self._prime_generator(func_name, func, pkt)
        else:
            self._prime_generator(func_name, func, pkt)


    def _prime_generator(self, func_name, func, pkt):
        gen = func(pkt)
        gen.next()
        self.in_progress[func_name] = gen
