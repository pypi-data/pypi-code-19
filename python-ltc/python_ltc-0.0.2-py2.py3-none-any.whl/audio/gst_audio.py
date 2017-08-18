import threading
import collections

try:
    import pgi
except ImportError:
    pgi = None

if pgi is not None:
    pgi.install_as_gi()

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

from pyltc.audio.base import AudioBackend
from pyltc.tcgen import AudioGenerator

class FakeContext(object):
    def __enter__(self):
        pass
    def __exit__(self, *args):
        pass

class GstAudio(AudioBackend):
    frames_per_queue = 10
    queue_length = 1
    aligned_chunk_size = 4096
    def __init__(self, **kwargs):
        self.aligned_buffer_queue = collections.deque()
        self.aligned_bytes_waiting = None
        super(GstAudio, self).__init__(**kwargs)
    def init_backend(self):
        GObject.threads_init()
        Gst.init('')

        self.emit_lock = threading.Lock()
        self.enable_push = False
        self.push_length = 0
        self.main_loop = None
        self.idle_id = None
        self.num_samples = 0
        self.buffer_waiting = None
        self.pipeline = self.build_pipeline()
    def _start(self):
        #self.idle_id = GObject.idle_add(self.push_data_to_element)
        self.pipeline.set_state(Gst.State.PLAYING)
    def run_loop(self):
        self.main_loop = GObject.MainLoop()
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop()
    def _stop(self):
        if self.main_loop is not None and self.main_loop.is_running():
            self.main_loop.quit()
            self.main_loop = None
        self.pipeline.set_state(Gst.State.NULL)
    def on_bus_message(self, bus, msg):
        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            print('Error from {}: {}'.format(msg.src.get_name(), err))
            print('Debug: {}'.format(debug))
        #print(str(msg.type))
    def build_pipeline(self):
        gen = self.generator
        if gen.bit_depth == 8:
            capstr = 'S8'
        else:
            capstr = 'S{}LE'.format(gen.bit_depth)
        pipeline = Gst.Pipeline.new('pipeline')
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_bus_message)
        capstr = 'audio/x-raw, format=(string){}, rate=(int){}, channels=(int)1'.format(capstr, gen.sample_rate)
        audcaps = Gst.caps_from_string(capstr)
        audsrc = self.src_element = Gst.ElementFactory.make('appsrc', 'audsrc')
        audq = Gst.ElementFactory.make('queue', 'audq')
        capfilt = Gst.ElementFactory.make('capsfilter', 'audcapfilt')
        wavenc = Gst.ElementFactory.make('wavenc', 'wavenc')
        aconv = Gst.ElementFactory.make('audioconvert', 'aoutconv')
        asamp = Gst.ElementFactory.make('audioresample', 'aresamp')
        aout = Gst.ElementFactory.make('autoaudiosink', 'auto_aout')
        capfilt.set_property('caps', audcaps)
        audprops = {
            'is-live':True,
            'max-bytes':gen.sample_rate,
            'min-percent':100,
            #'block':True,
            #'emit-signals':False,
            'caps':audcaps,
            'format':Gst.Format.BUFFERS,
        }
        print(audcaps.to_string())
        print(audsrc.get_property('format'))
        for key, val in audprops.items():
            audsrc.set_property(key, val)
        audsrc.connect('need-data', self.on_src_need_data)
        audsrc.connect('enough-data', self.on_src_enough_data)
        achain = [audsrc, audq, aconv, asamp, aout]
        for e in achain:
            pipeline.add(e)
        for i, e in enumerate(achain):
            try:
                next_e = achain[i+1]
            except IndexError:
                break
            e.link(next_e)
        return pipeline
    def push_data_to_element(self, *args):
        #with self.emit_lock:
        if not self.enable_push:
            return True
        length = self.push_length
        #if not length:
        #    return True
        bytes_queued = self.src_element.get_property('current-level-bytes')
        max_bytes = self.src_element.get_property('max-bytes')
        if bytes_queued + length > max_bytes:
            return True
        pushed = self._push_data_to_element(length)
        #self.push_length -= pushed
        return True
    def fill_buffer(self):
        super(GstAudio, self).fill_buffer()
        self.align_buffers()
    def next_buffer(self):
        if not len(self.aligned_buffer_queue):
            self.fill_buffer()
        return self.aligned_buffer_queue.popleft()
    def align_buffers(self):
        current_bytes = self.aligned_bytes_waiting
        chunk_size = self.aligned_chunk_size
        current_samples = self.num_samples
        def build_and_append(a, b):
            buffer = Gst.Buffer.new_wrapped(b)
            buffer.pts = Gst.util_uint64_scale(
                self.num_samples,
                Gst.SECOND,
                self.sample_rate,
            )
            buffer.duration = Gst.util_uint64_scale(
                a.size,
                Gst.SECOND,
                self.sample_rate,
            )
            self.aligned_buffer_queue.append(buffer)
            self.num_samples += a.size
        while True:
            try:
                a = self.queue.popleft()
            except IndexError:
                self.aligned_bytes_waiting = current_bytes
                break
            if current_bytes is None:
                current_bytes = a.tostring()
            else:
                current_bytes += a.tostring()
            current_size = len(current_bytes)
            if current_size == chunk_size:
                build_and_append(a, current_bytes)
                current_bytes = None
            elif current_size > chunk_size:
                aligned_bytes = current_bytes[:chunk_size]
                current_bytes = current_bytes[chunk_size:]
                build_and_append(a, aligned_bytes)
            current_samples += a.size
        #self.num_samples = current_samples
    def _push_data_to_element(self):
        buffer = self.next_buffer()
        buffer_size = buffer.get_size()
        #if length < buffer_size:
        #    self.buffer_waiting = buffer
        #    return 0

        resp = self.src_element.emit('push-buffer', buffer)
        print('push-buffer', buffer_size, resp)
        self.buffer_waiting = None
        return buffer_size
    def on_src_need_data(self, element, length):
        print('need-data', element, length)
        pushed = 0
        while pushed < length:
            pushed += self._push_data_to_element()

        # with self.emit_lock:
        #     self.push_length = length
        #     self.enable_push = True
        #     # if self.idle_id is not None:
        #     #     return
        #     # self.idle_id = GObject.idle_add(self.push_data_to_element, element, length)
    def on_src_enough_data(self, element):
        print('enough-data', element)
        return
        with self.emit_lock:
            print('lock acquired')
            #self.push_length = 0
            self.enable_push = False
            # idle_id = self.idle_id
            # if idle_id is None:
            #     return
            # self.idle_id = None
            # GObject.source_remove(idle_id)

def main(**kwargs):
    generator = AudioGenerator(
        frame_format={'rate':29.97, 'drop_frame':True},
        bit_depth=16,
    )
    aud = GstAudio(generator=generator)
    aud.start()
    aud.run_loop()

if __name__ == '__main__':
    main()
