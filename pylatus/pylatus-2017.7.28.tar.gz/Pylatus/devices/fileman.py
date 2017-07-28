#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import glob
import shutil
import bisect
from datetime import datetime
from multiprocessing import Process, Pipe
from PyQt5 import QtCore
from auxygen.devices.logger import Logger
from cryio import cbfimage
from ..controller.config import Config


def closest(date, dates):
    """Searches for the closest value to the 'date' parameters in 'dates' sorted list"""
    i = bisect.bisect_left(dates, date)
    if not i:
        date1, date2 = dates[0], dates[0]
    elif i >= len(dates):
        date1, date2 = dates[-1], dates[-1]
    else:
        date1, date2 = dates[i - 1:i + 1]
    diff1, diff2 = abs(date1 - date), abs(date2 - date)
    _min = min(diff1, diff2)
    return date1 if _min == diff1 else date2


class FileManagerProcess(Process):
    def __init__(self, opts):
        super().__init__()
        self.opts = opts
        self.oldCbf = set()
        self.newCbf = []

    def run(self):
        self.moveCbfFiles()
        self.writeCbfHeaders()

    def writeCbfHeaders(self):
        self.newCbf.sort()
        cryoTemps, blowerTemps, monitorValues, lakeshoreTemps = self.opts['pipe'].recv()
        cryoTempsKeys = sorted(cryoTemps.keys())
        blowerTempsKeys = sorted(blowerTemps.keys())
        monitorValuesKeys = sorted(monitorValues.keys())
        lakeshoreTempsKeys = sorted(lakeshoreTemps.keys())
        for i, cbfFile in enumerate(self.newCbf):
            cbf = cbfimage.CbfHeader(cbfFile)
            cbfTimestamp = cbf.get_timestamp()
            cryoValue = cryoTemps[closest(cbfTimestamp, cryoTempsKeys)] if cryoTempsKeys else 0
            blowerValue = blowerTemps[closest(cbfTimestamp, blowerTempsKeys)] if blowerTempsKeys else 0
            monitorValue = monitorValues[closest(cbfTimestamp, monitorValuesKeys)] if monitorValuesKeys else 0
            lakeshoreValue = lakeshoreTemps[closest(cbfTimestamp, lakeshoreTempsKeys)] if lakeshoreTempsKeys else 0
            if self.opts['oscAxis'] == 'PHI':
                omega = self.opts['omegaphi']
                omegaInc = 0
                phi = self.opts['startAngle']
                phiInc = self.opts['step']
            else:  # self.oscAxis == 'OMEGA'
                omega = self.opts['startAngle']
                omegaInc = self.opts['step']
                phi = self.opts['omegaphi']
                phiInc = 0
            cbf.header_dict.update({'Start_angle': self.opts['startAngle'], 'Angle_increment': self.opts['step'],
                                    'Omega': omega, 'Omega_increment': omegaInc, 'Phi': phi, 'Phi_increment': phiInc,
                                    'Kappa': self.opts['kappa'], 'Oscillation_axis': self.opts['oscAxis'],
                                    'Flux': monitorValue, 'Temperature': cryoValue, 'Blower': blowerValue,
                                    'Lakeshore': lakeshoreValue})
            cbf.save_cbf(cbfFile)
            self.opts['startAngle'] += self.opts['step']
        self.opts['pipe'].send((cryoTempsKeys, blowerTempsKeys, monitorValuesKeys, lakeshoreTempsKeys))
        self.opts['pipe'].close()

    def moveCbfFiles(self):
        self.genOldCbf()
        while self.oldCbf:
            time.sleep(0.1)
            for f in os.listdir(self.opts['dataDir']):
                try:
                    self.doMove(f)
                except OSError:
                    continue

    def doMove(self, f):
        oldcbf = os.path.join(self.opts['dataDir'], f)
        newcbf = os.path.join(self.opts['path'], f)
        # we touch only the files which are older than the certain time, when the user pressed the start button
        # otherwise we could process files from the previous aborted data collection
        if f in self.oldCbf and cbfimage.CbfHeader(oldcbf).dateTime() >= self.opts['startTime']:
            shutil.move(oldcbf, newcbf)
            self.oldCbf.remove(f)
            self.newCbf.append(newcbf)

    def genOldCbf(self):
        for i in range(self.opts['nframes']):
            if self.opts['nframes'] > 1:
                cbfName = f'{self.opts["cbf"]}_{i:05d}.cbf'
            else:
                cbfName = f'{self.opts["cbf"]}.cbf'
            self.oldCbf.add(cbfName)


class FileManager(QtCore.QObject):
    sigProcessFinished = QtCore.pyqtSignal(tuple, str, int)
    sigFileError = QtCore.pyqtSignal(str)
    sigDirError = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = Logger('Fileman')
        self.queue = {}
        self.timer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.checkProcesses)
        self.timer.setInterval(500)
        self.timer.start()

    def stop(self):
        """
        This is the full stop procedure to shut down processes.
        To abort the current experiment the FileManager.abort(process) must be used.
        """
        for process in list(self.queue):
            self.queue[process]['pipe'].close()
            process.terminate()
            process.join()
            del self.queue[process]

    def startNewProcess(self, opts):
        if not os.path.exists(Config.DataDir):
            self.logger.error(f'Data dir {Config.DataDir} does not exist. Please fix it before continue.')
            return
        path = os.path.join(Config.UserDir, opts['userSubDir'])
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as err:
            self.logger.error(f'Cannot create user directory {path}: {err}')
            return
        pipe0, pipe1 = Pipe()
        opts['cbf'] = opts['cbfName'][:-4]
        opts.update({'dataDir': Config.DataDir, 'path': path, 'pipe': pipe1, 'startTime': datetime.now()})
        process = FileManagerProcess(opts)
        self.queue[process] = {'pipe': pipe0, 'stop': False, 'data': None, 'dir': opts['userSubDir'],
                               'period': opts['period']}
        process.start()
        return process

    def feedCbfValues(self, process, data):
        if process in self.queue:
            self.queue[process]['data'] = data

    def abort(self, process):
        if process in self.queue:
            self.queue[process]['stop'] = True

    def checkProcesses(self):
        for process in list(self.queue):
            # we have data (temperatures, monitors) from the main thread, so put them to the pipe
            if self.queue[process]['data']:
                self.queue[process]['pipe'].send(self.queue[process]['data'])
                self.queue[process]['data'] = None
            # the process is finished, we receive info from it to clean old temperatures and monitors
            elif self.queue[process]['pipe'].poll():
                oldData = self.queue[process]['pipe'].recv()
                period = self.queue[process]['period']
                dirr = self.queue[process]['dir']
                self.sigProcessFinished.emit(oldData, dirr, period)
                self.queue[process]['pipe'].close()
                process.join()
                del self.queue[process]
            # user has stopped the measurements, we need to terminate the child process
            elif self.queue[process]['stop']:
                self.queue[process]['pipe'].close()
                process.terminate()
                process.join()
                del self.queue[process]

    def clean(self, dataDir):
        if os.path.exists(dataDir):
            for path in glob.iglob(f'{dataDir}/*'):
                try:
                    os.remove(path)
                except IsADirectoryError:
                    self.sigDirError.emit(f'There is a directory on the camserver ramdisk!\n{path}\n'
                                          f'Normally, it should not happen. Probably, it was BCU.\n'
                                          f'Please, remove it manually.')
                except PermissionError:
                    self.sigFileError.emit(f'Pylatus do not have enough permissions in {dataDir}.\n'
                                           f'Please check it. Exiting...')
                    return
