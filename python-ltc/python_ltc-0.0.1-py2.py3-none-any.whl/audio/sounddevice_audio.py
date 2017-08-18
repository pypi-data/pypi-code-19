import time
import threading
import collections

import numpy as np
import sounddevice as sd

from pyltc.audio.base import AudioBackend
from pyltc.tcgen import AudioGenerator

class SampleQueue(object):
    def __init__(self, **kwargs):
        self.block_size = kwargs.get('block_size')
        self.queue_length = kwargs.get('queue_length')
        self.dtype = kwargs.get('dtype')
        self.queue = np.zeros((self.queue_length, self.block_size), dtype=self.dtype)
        self.num_items = 0
        self.last_block = None
        self.index = 0
        self.append_index = 0
    def append(self, block):
        if self.last_block is not None:
            #print('last_block={}, block={}'.format(self.last_block.size, block.size))
            block = np.concatenate((self.last_block, block))
            self.last_block = None
        size = block.size
        if size < self.block_size:
            self.last_block = block
            #print('too small: {}'.format(size))
        elif size == self.block_size:
            self._do_append(block)
            #print('just right: {}'.format(size))
        else:
            last_block = block[self.block_size:]
            block = block[:self.block_size]
            self._do_append(block)
            #print('too big: block={}, last_block={}'.format(block.size, last_block.size))
            self.append(last_block)
        #print('append queue_length: {}'.format(len(self.queue)))
    def _do_append(self, block):
        self.queue[self.append_index][:] = block
        self.num_items += 1
        self.append_index += 1
        if self.append_index >= self.queue_length:
            self.append_index = 0
    def popleft(self):
        if not self.num_items:
            raise IndexError('pop from an empty queue')
        a = self.queue[self.index]
        self.num_items -= 1
        self.index += 1
        if self.index >= self.queue_length:
            self.index = 0
        return a
    def __len__(self):
        return self.num_items

class SdAudio(AudioBackend):
    block_size = 512
    buffer_length = 16384
    queue_length = 16
    def __init__(self, **kwargs):
        self.stream_buffer = None
        self.next_block = None
        self._lock = threading.Lock()
        super(SdAudio, self).__init__(**kwargs)
        self.queue = SampleQueue(
            block_size=self.block_size,
            queue_length=self.queue_length,
            dtype=self.generator.sampler.dtype,
        )
        spf = int(self.generator.samples_per_frame)
        fpq = int(self.block_size // spf)
        if fpq * spf < self.block_size:
            fpq += 1
        self.frames_per_queue = fpq
    # def fill_buffer(self):
    #     if self.stream_buffer is None:
    #         self.stream_buffer = self.get_frames()
    #     while self.stream_buffer.size < self.buffer_length:
    #         a = self.get_frames()
    #         with self._lock:
    #             self.stream_buffer = np.concatenate((self.stream_buffer, a))
    # def popleft(self):
    #     #with self._lock:
    #     self.block_thread.work_complete.wait()
    #     a = self.next_block
    #     self.next_block = None
    #     if self.block_thread is not None:
    #         self.block_thread.need_data.set()
    #     #a = self.next_block
    #     #self.prepare_next_block()
    #     return a
    def prepare_next_block(self):
        #with self._lock:
        if self.next_block is not None:
            return
        size = self.block_size
        with self._lock:
            self.next_block = self.stream_buffer[:size]
            self.stream_buffer = self.stream_buffer[size:]
        self.buffer_thread.need_data.set()
    def init_backend(self):
        sd.default.samplerate = self.sample_rate
        sd.default.channels = 1

        self.buffer_thread = BufferThread(backend=self)
        #self.block_thread = NextBlockThread(backend=self)
    def _start(self):
        self.preroll = True
        self.num_callbacks = 0
        self.sd_stream = sd.OutputStream(
            dtype=self.generator.sampler.dtype,
            blocksize=self.block_size,
            callback=self.stream_callback,
            prime_output_buffers_using_stream_callback=True,
        )
        print('queue_length before start: {}'.format(len(self.queue)))
        self.buffer_thread.start()
        self.buffer_thread.work_complete.wait()
        #self.buffer_thread.running.wait()
        #self.block_thread.start()
        #self.block_thread.work_complete.wait()
        #self.block_thread.running.wait()
        self.sd_stream.start()
        self.preroll = False
    def run_loop(self):
        try:
            while True:
                sd.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        #start_ts = time.time()
        #sd.wait()
        #print('sd.wait complete')
        #while time.time() - start_ts < 10:
        #    time.sleep(1)
        #if self.buffer_thread is not None:
        #    self.buffer_thread.stop()
        #    self.buffer_thread = None
        # if self.block_thread is not None:
        #     self.block_thread.stop()
        #     self.block_thread = None
        self.stop()
        print('num_callbacks: ', self.num_callbacks)
    def _stop(self):
        self.sd_stream.stop()
        sd.stop()
        if self.buffer_thread is not None:
            self.buffer_thread.stop()
            self.buffer_thread = None
        # if self.block_thread is not None:
        #     self.block_thread.stop()
        #     self.block_thread = None
    def stream_callback(self, outdata, num_samples, t, status):
        #print('{}\tstream_callback'.format(time.time()))
        #print(len(self.queue))
        #if status:
        #    print(status)
        a = self.queue.popleft()
        #self.buffer_thread.need_data.set()
        #if self.preroll:
        #    self.num_callbacks += 1
        #print(num_samples, a.size)
        outdata[:, 0] = a

class BufferThreadBase(threading.Thread):
    def __init__(self, **kwargs):
        super(BufferThreadBase, self).__init__()
        self.running = threading.Event()
        self.stopped = threading.Event()
        self.need_data = threading.Event()
        self.work_complete = threading.Event()
        self.backend = kwargs.get('backend')
        rs = self.backend.sample_rate
        block_size = self.backend.block_size
        self.wait_timeout = 1. / rs * float(block_size) / 4
        print('wait_timeout: {}'.format(self.wait_timeout))
    def run(self):
        self.running.set()
        self._do_work()
        while self.running.is_set():
            self.need_data.wait(self.wait_timeout)
            self.need_data.clear()
            self._do_work()
            if not self.running.is_set():
                break
        self.stopped.set()
    def stop(self):
        self.running.clear()
        self.need_data.set()
        self.stopped.wait()
    def _do_work(self):
        self.work_complete.clear()
        #t = time.time()
        #print('{}\t{} starting'.format(t, self.__class__.__name__))
        self.do_work()
        self.work_complete.set()
        #t = time.time()
        #print('{}\t{} complete'.format(t, self.__class__.__name__))
    def do_work(self):
        pass

class BufferThread(BufferThreadBase):
    def do_work(self):
        #if len(self.backend.queue) < self.backend.queue_length:
        #    print(len(self.backend.queue))
        self.backend.fill_buffer()

class NextBlockThread(BufferThreadBase):
    def do_work(self):
        self.backend.prepare_next_block()

def main(**kwargs):
    generator = AudioGenerator(
        frame_format={'rate':29.97, 'drop_frame':True},
        bit_depth=16,
        sample_rate=22050,
    )
    aud = SdAudio(generator=generator)
    aud.start()
    aud.run_loop()

if __name__ == '__main__':
    main()
