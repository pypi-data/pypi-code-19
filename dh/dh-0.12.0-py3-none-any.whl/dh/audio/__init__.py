"""
Functions for audio handling and processing.

All audio signals are represented NumPy arrays (in the form `x[t]` for mono
signals and `x[t, channel]` for non-mono signals).
"""

import abc
import itertools
import math
import wave

import numpy as np
import pyaudio
import scipy.io.wavfile
import scipy.signal

import dh.utils
import dh.image


###
#%% input & output
###


def load(filename):
    (rate, data) = scipy.io.wavfile.read(filename=filename)
    return (rate, data)


def save(filename, data, rate=44100):
    scipy.io.wavfile.write(filename=filename, rate=rate, data=data)


class Recorder(abc.ABC):
    _DTYPES = {
        "int8":  {"bytes": 1, "pyaudio": pyaudio.paInt8, "numpy": "int8"},
        "int16": {"bytes": 2, "pyaudio": pyaudio.paInt16, "numpy": "int16"},
        "int32": {"bytes": 4, "pyaudio": pyaudio.paInt32, "numpy": "int32"},
    }

    def __init__(self, channelCount=2, rate=44100, dtype="int16", chunkSize=1024):
        """
        Records audio from a microphone. The data type `dtype` must be one of
        "int8", "int16", "int32".
        """
        self.channelCount = channelCount
        self.rate = rate
        self.dtype = dtype
        self.chunkSize = chunkSize
        assert self.dtype in Recorder._DTYPES.keys()

    def _durationToChunkCount(self, duration=None):
        """
        For a given duration in seconds, returns the number of full chunks that
        fit into this time span (or `None`, if duration is `None`).
        """
        if duration is None:
            return None
        else:
            chunksPerSecond = self.rate / self.chunkSize
            return math.ceil(chunksPerSecond * duration)

    def chunks(self, maxCount=None):
        """
        Generator which yields chunks of data. If `maxCount` is a number, the
        generator stops after that many chunks have been returned.
        """
        # set up PyAudio stream
        p = pyaudio.PyAudio()
        stream = p.open(
            format=Recorder._DTYPES[self.dtype]["pyaudio"],
            channels=self.channelCount,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunkSize,
        )

        # record and yield data, chunk-wise
        for nChunk in itertools.count():
            if (maxCount is None) or (nChunk < maxCount):
                yield stream.read(self.chunkSize)
            else:
                break

        # shutdown PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()


class WavRecorder(Recorder):
    def record(self, filename, duration=None):
        """
        Record audio and simultaneously save it to the WAV-file named
        `filename`. `duration` gives the recording time in seconds
        (infinite if `None`).
        """

        chunks = self.chunks(maxCount=self._durationToChunkCount(duration))
        with wave.open(filename, "wb") as wav:
            wav.setnchannels(self.channelCount)
            wav.setsampwidth(Recorder._DTYPES[self.dtype]["bytes"])
            wav.setframerate(self.rate)
            for chunk in chunks:
                wav.writeframes(chunk)


class NumpyRecorder(Recorder):
    def record(self, duration=None):
        pass

    def stream(self, length=1.0):
        frameCount = round(self.rate * length)

        numpyDtype = Recorder._DTYPES[self.dtype]["numpy"]
        x = np.zeros(shape=(0, self.channelCount), dtype=numpyDtype)
        chunks = self.chunks()
        for chunk in chunks:
            # get chunk and convert it to NumPy array
            c = np.fromstring(chunk, dtype=numpyDtype)
            c.shape = (self.chunkSize, self.channelCount)

            # add chunk to the data array and remove data older than `length`
            x = np.vstack([x, c])
            x = x[max(0, x.shape[0] - frameCount):, :]

            yield x


###
#%% data type and mode handling
###


def trange(dtype):
    """
    Returns the range (min, max) of valid intensity values for an audio signal
    of NumPy type string `dtype`.

    Allowed types are `'int8'`, `'int16'`, `'int32'`, and any float type
    (e.g., `'float32'`, `'float64'`).

    >>> trange('int8')
    (-128, 127)
    >>> trange('float32')
    (-1.0, 1.0)
    """

    if dtype is None:
        # np.issubdtype(None, "float") is True, therefore we have to check for this error here explicitly
        raise ValueError("Invalid image type '{dtype}'".format(dtype=dtype))
    elif dtype == "int8":
        return (-128, 127)
    elif dtype == "int16":
        return (-32768, 32767)
    elif dtype == "int32":
        return (-2147483648, 2147483647)
    elif np.issubdtype(dtype, "float"):
        return (-1.0, 1.0)
    else:
        raise ValueError("Unsupported data type '{dtype}'".format(dtype=dtype))


def convert(x, dtype):
    """
    Converts audio signal `s` to NumPy type given by the string `dtype` and
    scales the values accordingly.

    The values are always clipped to the allowed range (even for identical
    source and target types). Returns always a copy of the data, even for equal
    source and target types.
    """

    # clip image against its source dtype (important for floats)
    (lowerOld, upperOld) = trange(x.dtype)
    y = clip(x, lowerOld, upperOld)

    if x.dtype == dtype:
        return y
    else:
        (lowerNew, upperNew) = trange(dtype)
        return ((y.astype("float") - lowerOld) / (upperOld - lowerOld) * (upperNew - lowerNew) + lowerNew).astype(dtype)


###
#%% element-wise operations
###


def clip(x, lower=None, upper=None):
    """
    Clips the signal values to the interval [`lower`, `upper`], and preserves
    the data type.

    Always returns a copy of the data, even if both interval ends are `None`.
    """

    y = x.copy()
    dtype = y.dtype
    (tLower, tUpper) = trange(dtype)
    if lower is not None:
        y = np.maximum(y, np.array((dh.utils.sclip(lower, tLower, tUpper),), dtype=dtype))
    if upper is not None:
        y = np.minimum(y, np.array((dh.utils.sclip(upper, tLower, tUpper),), dtype=dtype))
    return y


###
#%% feature transforms
###


def spectrogram(x, rate):
    y = convert(x[:, 0], "float")
    res = scipy.signal.spectrogram(y, fs=rate, mode="magnitude")
    S = res[2]
    S = S[::-1, :]
    return S


def main():
    #R = WavRecorder(rate=44100 // 4)
    #R.record("test6.wav", 1.0)
    recorder = NumpyRecorder(chunkSize=1024 * 1, rate=44100 // 4)
    for x in recorder.stream(2.5):
        S = spectrogram(x, recorder.rate)
        dh.image.pinfo(S)
        #S = dh.image.normalize(S, "minmax")

        S = S * 1.0

        S = dh.image.clip(S, 0.0, 1.0)
        #S = dh.image.log(S)
        #S = S ** 0.125
        #S = dh.image.convert(S, "uint8")
        #S = S / 16.0
        #dh.image.pinfo(S)
        #
        #S = dh.image.colorize(S, "afmhot")
        key = dh.image.show(S, wait=10)
        if key in dh.utils.qkeys():
            return
        elif key == ord("c"):
            dh.image.cdemo(S)


if __name__ == "__main__":
    main()

