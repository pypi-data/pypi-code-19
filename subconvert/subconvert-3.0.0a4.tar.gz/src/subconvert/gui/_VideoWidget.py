"""
Copyright (C) 2011, 2012, 2013 Michal Goral.

This file is part of Subconvert

Subconvert is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Subconvert is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Subconvert. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import mpv

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSlider, QPushButton, QSizePolicy
from PyQt5.QtWidgets import QAbstractSlider, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl, QTimer

from subconvert.parsing.FrameTime import FrameTime
from subconvert.utils.SubSettings import SubSettings
from subconvert.utils.SubFile import File
from subconvert.utils.cleanup import cleanup

from subconvert.utils.Locale import _

# NOTE: mpv's commands, options and properties are described here:
#
#     http://mpv.io/manual/master/#options
#     http://mpv.io/manual/master/#list-of-input-commands
#     http://mpv.io/manual/master/#properties
#
# NOTE: mpv module by default starts one thread for event handling (functions
# called by player.observe_property are called on a different thread).


class VideoWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._initWidget()
        self._timer = QTimer(self)
        self._loadedFps = None
        self._prevPos = None

        # mpv state observers
        self._player.observe_property('duration', self._durationChanged)
        self._player.observe_property('pause', self._pauseChanged)

        # connect some signals
        self._playButton.clicked.connect(self._playButtonToggled)
        self._slider.actionTriggered.connect(self._sliderActionHandle)

        # we could observe mpv's time-pos property, but after 5-10 seconds of
        # very frequent updates displaying time value totally breaks.
        self._timer.timeout.connect(self._updatePosition)

        cleanup.register(self._cleanup)

    @property
    def real(self):
        '''Or is it fantasy?'''
        return True

    def show(self):
        super().show()

    def hide(self):
        self.pause()
        super().hide()

    def play(self):
        self._player.pause = False
        self._timer.start(150)

    def pause(self):
        self._player.pause = True
        self._timer.stop()

    @property
    def playing(self):
        '''Tells whether there's a movie currently being played.'''
        # It's more complicated than simply returning whether movie is paused.
        # E.g. if there's no movie loaded, it isn't "paused" (player.pause is
        # False), but it isn't playing either.
        return self._player.time_pos is not None and not self._player.pause

    def togglePlayback(self):
        if self._player.pause:
            self.play()
        else:
            self.pause()

    def nextFrame(self):
        self._player.frame_step()
        self._updatePosition()

    def prevFrame(self):
        self._player.frame_back_step()
        self._updatePosition()

    def seek(self, ms, mode='relative'):
        if not self._player.seekable:
            return
        self._player.seek(ms / 1000, mode)
        self._updatePosition()

    def forward(self):
        self.seek(5000)

    def rewind(self):
        self.seek(-5000)

    def fastForward(self):
        self.seek(30000)

    def fastRewind(self):
        self.seek(-30000)

    def jumpTo(self, frametime):
        self.seek(frametime.ms, mode='absolute')

    @property
    def position(self):
        ms = round(1000 * self._player.time_pos)
        return FrameTime(ms, self._fps)

    def openFile(self, filePath):
        self._reset()
        self._slider.setDisabled(False)

        state = self.playing
        self._player.play(filePath)
        self.play() if state else self.pause()
        self.show_text(os.path.basename(filePath))

    def loadSubtitles(self, subtitles):
        pass

    def show_text(self, text, duration=5000):
        self._player.show_text(text, duration)

    @property
    def videoPath(self):
        return self._player.path

    def _initWidget(self):
        self.setObjectName("video_player")

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Separate background to keep black background when playerWidget resizes
        self._background = QWidget(self)
        self._background.setStyleSheet("background: black")
        mainLayout.addWidget(self._background, 1)

        self._player = mpv.MPV()
        self._playerWidget = QWidget()
        self._player.osc = False
        self._player.sub_auto = 'no'
        self._player.keep_open = 'always'
        self._player.wid = int(self._playerWidget.winId())

        backgroundLayout = QHBoxLayout()
        backgroundLayout.setContentsMargins(0, 0, 0, 0)
        self._background.setLayout(backgroundLayout)
        backgroundLayout.addWidget(self._playerWidget)

        controls = self._initControlPanel()
        mainLayout.addLayout(controls)

        self.setLayout(mainLayout)

    def _initControlPanel(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self._playButton = QPushButton(QIcon.fromTheme("media-playback-start"), "", self)
        self._playButton.setCheckable(True)
        self._playButton.setFocusPolicy(Qt.NoFocus)
        self._playButton.setToolTip(_("Play/Pause"))
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setDisabled(True)
        self._slider.setRange(0, 0)
        self._timeLabel = QLabel("0:00:00.000", self)
        layout.addWidget(self._playButton)
        layout.addWidget(self._slider)
        layout.addWidget(self._timeLabel)
        layout.addSpacing(5)
        return layout

    def saveWidgetState(self, settings):
        settings = SubSettings()
        settings.setHidden(self, self.isHidden())

    def restoreWidgetState(self, settings):
        if settings.getHidden(self) is True:
            self.hide()
        else:
            self.show()

    def _sliderActionHandle(self, action):
        if action == QAbstractSlider.SliderPageStepAdd:
            self.seek(1000)
        elif action == QAbstractSlider.SliderPageStepSub:
            self.seek(-1000)
        elif action == QAbstractSlider.SliderSingleStepAdd:
            self.forward()
        elif action == QAbstractSlider.SliderSingleStepSub:
            self.rewind()
        elif action == QAbstractSlider.SliderMove:
            position = self._slider.sliderPosition()
            self.seek(position, mode='absolute')
            if self._slider.isSliderDown():
                # TODO: extract conversion of ms to formatted time outside of
                # FrameTime (or as its staticmethod)
                ft = FrameTime(position, 1)
                self._timeLabel.setText(ft.toStr())

    def _durationChanged(self, name, duration):
        if not duration:
            self._slider.setRange(0, 0)
        else:
            self._slider.setRange(0, round(duration * 1000))

    def _playButtonToggled(self, checked):
        if checked is True:
            self.play()
        else:
            self.pause()

    def _pauseChanged(self, name, paused):
        if paused:
            self._playButton.setChecked(False)
            if self._player.eof_reached:
                self.seek(0, mode='absolute')
                self._updatePosition()
        else:
            self._playButton.setChecked(True)
            self._updatePosition()

    def _updatePosition(self):
        pos = self._player.time_pos
        if pos is not None:
            ms = round(1000 * pos)

            if not self._slider.isSliderDown():
                self._slider.setValue(ms)
                # TODO: extract conversion of ms to formatted time outside of
                # FrameTime (or as its staticmethod)
                ft = FrameTime(ms, 1)
                self._timeLabel.setText(ft.toStr())

    @property
    def _fps(self):
        if self._loadedFps is None:
            self._loadedFps = File.detectFpsFromMovie(self.videoPath).fps
        return self._loadedFps

    def _reset(self):
        self._loadedFps = None
        self._prevPos = None
        self._timeLabel.setText(FrameTime(0, 1).toStr())

    def _cleanup(self):
        self._player.terminate()
