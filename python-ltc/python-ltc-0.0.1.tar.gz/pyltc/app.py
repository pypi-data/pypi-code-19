
import numpy as np

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    ObjectProperty,
    StringProperty,
    NumericProperty,
    BooleanProperty,
)
from kivy.uix.boxlayout import BoxLayout

from pyltc.tcgen import AudioGenerator
from pyltc.audio.pyjack_audio import JackAudio

class LTCViewerApp(App):
    generator = ObjectProperty(None, allownone=True)
    audio_backend = ObjectProperty(None, allownone=True)
    running = BooleanProperty(False)
    clock_event = ObjectProperty(None, allownone=True)
    hours = NumericProperty(0)
    minutes = NumericProperty(0)
    seconds = NumericProperty(0)
    frames = NumericProperty(0)
    def run_generator(self):
        if self.running:
            return
        self.running = True
        self.generator = AudioGenerator(
            frame_format={'rate':29.97, 'drop_frame':True},
            frame_callback=self.frame_callback,
            bit_depth=32,
            use_float_samples=True,
            dtype=np.dtype(np.float32),
            sample_rate=48000,
        )
        self.audio_backend = JackAudio(generator=self.generator)
        self.audio_backend.start()
        self.clock_event = Clock.schedule_interval(self.wait_for_frame, 1 / 29.97)
        return True
    def stop_generator(self):
        if not self.running:
            return
        if self.clock_event is not None:
            Clock.unschedule(self.clock_event)
            self.clock_event = None
        if self.audio_backend is not None:
            self.audio_backend.stop()
            self.audio_backend = None
        self.generator = None
        self.running = False
    def wait_for_frame(self, *args):
        self.frame_callback()
    def frame_callback(self, *args):
        g = self.generator
        if g is None:
            return
        f = g.frame
        self.hours = int(f.hour.value)
        self.minutes = int(f.minute.value)
        self.seconds = int(f.second.value)
        self.frames = int(f.value)


class Digit(BoxLayout):
    app = ObjectProperty(None)
    attr = StringProperty()
    tens = NumericProperty()
    units = NumericProperty()
    def on_app(self, *args):
        self.bind_attr()
    def on_attr(self, *args):
        self.bind_attr()
    def bind_attr(self):
        if self.app is None:
            return
        if not self.attr:
            return
        self.app.bind(**{self.attr:self._on_value})
    def _on_value(self, instance, value):
        self.tens = int(value // 10)
        self.units = value % 10

def run_app(**kwargs):
    LTCViewerApp().run()

if __name__ == '__main__':
    run_app()
