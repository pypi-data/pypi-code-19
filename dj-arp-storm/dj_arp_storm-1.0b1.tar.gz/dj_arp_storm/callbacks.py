class CallbackBase(object):

    def __init__(self, sounds):
        self.sounds = sounds
        self.in_progress = {}

    def _call(self, func, bpf, pkt):
        hash = str(func)+bpf
        cb = self.in_progress.get(hash)
        if cb:
            try:
                cb.send(pkt)
            except StopIteration:
                    self._prime_generator(hash, func, pkt)
        else:
            self._prime_generator(hash, func, pkt)


    def _prime_generator(self, hash, func, pkt):
        gen = func(pkt)
        gen.next()
        self.in_progress[hash] = gen
