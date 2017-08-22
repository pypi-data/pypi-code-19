#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname
from os.path import join as pjoin

from PIL.Image import Image
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QFrame, QFileDialog, QApplication

from mtb.video_prop import Video
from mtb.qtWidgets import ListWidgetItem, ImageComp, Button
from mtb.utils import Folder

assets = pjoin(dirname(__file__), 'assets')
from concurrent.futures import ThreadPoolExecutor


class videoListWidgetItem(ListWidgetItem):
    def __init__(self, name, path):
        super(videoListWidgetItem, self).__init__(name, path)


class LUTComp(ImageComp):
    def __init__(self, ctrls=False):
        super(LUTComp, self).__init__(ctrls=ctrls)

        self.setMinimumSize(640, 360)


class LUTWrapper(QWidget):
    def __init__(self, parent=None):

        super(LUTWrapper, self).__init__(parent=parent)
        self.video = Video(None)
        self.videoLUT = Video(None)
        self.setStyleSheet("background-color:rgb(40,40,40);color:rgb(220,218,215)")

        # Cache
        self.current_frame = 1
        self.current_LUT = None

        self.LUT = None

        self.buildUI()
        self.executor = ThreadPoolExecutor(max_workers=8)

    def buildUI(self):
        layout = QVBoxLayout(self)

        self.view = LUTComp()
        layout.addWidget(self.view)

        ctrl_layout = QHBoxLayout()

        self.buttonPrevious = Button("<")
        self.buttonNext = Button(">")

        ctrl_layout.addWidget(self.buttonPrevious)
        ctrl_layout.addWidget(self.buttonNext)

        layout.addLayout(ctrl_layout)

        list_layout = QHBoxLayout()
        LUT_layout = QVBoxLayout()
        FILE_layout = QVBoxLayout()

        list_layout.addLayout(LUT_layout)
        list_layout.addLayout(FILE_layout)

        # LUT LIST
        self.lutList = QListWidget()

        self.lutList.setFocusPolicy(Qt.StrongFocus)
        self.lutList.setStyleSheet("font-family:Akkurat-Mono;background-color:rgba(0,0,0,0);border:none")

        self.buttonLUTbrowse = Button("Load")

        LUT_layout.addWidget(self.lutList)
        LUT_layout.addWidget(self.buttonLUTbrowse)
        # FILE LIST
        self.fileList = QListWidget()
        self.fileList.setStyleSheet("font-family:Akkurat-Mono;background-color:rgba(0,0,0,0);border:none")
        self.fileList.setFrameStyle(QFrame.NoFrame)
        self.fileList.setFocusPolicy(Qt.StrongFocus)

        self.buttonFILEBrowse = Button("Load")

        FILE_layout.addWidget(self.fileList)
        FILE_layout.addWidget(self.buttonFILEBrowse)

        layout.addLayout(list_layout)

        # signals linking
        self.lutList.currentItemChanged.connect(self.listLUT)
        self.fileList.currentItemChanged.connect(self.listVideo)

        self.buttonLUTbrowse.leftClick.connect(self.loadLUTS)
        self.buttonFILEBrowse.leftClick.connect(self.loadVideos)

        self.buttonPrevious.leftClick.connect(self.previousFrame)
        self.buttonNext.leftClick.connect(self.nextFrame)

    # LUTS PATH
    @property
    def luts_path(self):
        return self._luts_path

    @luts_path.setter
    def luts_path(self, lutdirpath):

        self.lutList.clear()
        lutfilter = Folder(lutdirpath)
        lutfilter.accepted_types = [".cube"]
        lutfilter.recursive = True

        for l in lutfilter.files:
            l = ListWidgetItem(l.name.replace(l.suffix, ""), str(l.resolve()))
            self.lutList.addItem(l)

    # VIDEO PATH
    @property
    def videos_path(self):
        return self._videos_path

    @videos_path.setter
    def videos_path(self, videopath):

        self.fileList.clear()
        f = Folder(videopath)
        f.accepted_types = [".MOV", ".mp4", ".mov"]

        for x in f.files:
            x = ListWidgetItem(x.name.replace(x.suffix, ""), str(x.resolve()))
            self.fileList.addItem(x)

        self.current_video = f.files[0]
        self._videos_path = f

    # CURRENT LUT
    @property
    def current_LUT(self):
        return self._current_LUT

    @current_LUT.setter
    def current_LUT(self, lutpath):

        if self.videoLUT.LUT == lutpath:
            return

        self.videoLUT.LUT = lutpath
        self._current_LUT = lutpath
        if not lutpath:
            return
        print("Reading Lut: {}".format(self.videoLUT.lut_name))
        self.readLUTFrame()

    # CURRENT VIDEO
    @property
    def current_video(self):
        return self._current_video

    @current_video.setter
    def current_video(self, currentvideo):

        # TODO: save the previous frame to cache here!

        try:
            if self.video.file == currentvideo:
                return
        except:
            pass

        self.video = Video()
        self.videoLUT = Video()

        self.video.file = currentvideo
        self.videoLUT.file = currentvideo

        self._current_video = currentvideo

        self.readFrame()
        self.readLUTFrame()

        if self.lutList.selectedItems():
            lutpath = self.lutList.selectedItems()[0].path
            self.current_LUT = lutpath

        else:
            print("No selected LUT")

    # CURRENT FRAME
    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, frame):
        self._current_frame = frame

    # FUNCTIONS
    def readFrame(self):
        # read video frame with callback.
        current_call = self.video.readFrame(self.frameReady)
        if type(current_call) == Image:
            self.view.A = current_call
            self.buttonNext.setStyleSheet(self.buttonNext.cOff)
            self.buttonPrevious.setStyleSheet(self.buttonNext.cOff)
        else:
            self.current_process = self.executor.submit(current_call.wait)

    def readLUTFrame(self):
        # read video frame with callback.
        current_call = self.videoLUT.readFrame(self.frameReadyLUT)
        print(current_call)
        if type(current_call) == Image:
            self.view.B = current_call
            self.buttonNext.setStyleSheet(self.buttonNext.cOff)
            self.buttonPrevious.setStyleSheet(self.buttonNext.cOff)
        else:
            self.current_process = self.executor.submit(current_call.wait)

    def frameReadyLUT(self):

        self.view.B = self.videoLUT.frame
        self.buttonNext.setStyleSheet(self.buttonNext.cOff)
        self.buttonPrevious.setStyleSheet(self.buttonNext.cOff)

    def frameReady(self):
        self.view.A = self.video.frame

    # SIGNAL & EVENTS
    def listLUT(self, currentItem, previousItem):
        self.current_LUT = currentItem.path
        if self.videoLUT.LUT:
            self.setWindowTitle("Current LUT: {}".format(self.videoLUT.lut_name))

    def listVideo(self, currentItem, previousItem):
        self.current_video = currentItem.path

    def loadVideos(self):
        f = QFileDialog.getExistingDirectory(None, "Open Video Folder...")
        if f:
            self.videos_path = f

    def loadLUTS(self):
        f = QFileDialog.getExistingDirectory(None, "Open LUT Folder...")
        if f:
            self.luts_path = f

    def previousFrame(self):
        self.buttonPrevious.setStyleSheet(self.buttonPrevious.cOn)
        self.video.tc.add_frames(-25)
        self.videoLUT.tc.add_frames(-25)

        self.readFrame()
        self.readLUTFrame()

    def nextFrame(self):
        self.buttonNext.setStyleSheet(self.buttonNext.cOn)
        self.video.tc.add_frames(25)
        self.videoLUT.tc.add_frames(25)

        self.readFrame()
        self.readLUTFrame()
