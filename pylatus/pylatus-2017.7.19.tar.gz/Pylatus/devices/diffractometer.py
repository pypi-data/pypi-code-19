#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from PyQt5 import QtCore
import aspic
import auxygen
from ..controller import utils
from ..gui.gutils import GUtils
from . import scanman, fileman, musst, pilatus, monitor
from ..controller.config import Config


class Diffractometer(QtCore.QObject):
    sigMotorMoved = QtCore.pyqtSignal(str, float)
    sigWavelength = QtCore.pyqtSignal(float, float)
    sigExperimentFinished = QtCore.pyqtSignal()
    sigExperimentStarted = QtCore.pyqtSignal()
    sigFeedFileman = QtCore.pyqtSignal(object, object)
    sigStopFileman = QtCore.pyqtSignal()
    sigNoMonitorCounts = QtCore.pyqtSignal(bool)
    sigExperimentPaused = QtCore.pyqtSignal()
    sigExperimentResumed = QtCore.pyqtSignal()
    sigAllMotorsStopped = QtCore.pyqtSignal()
    sigMotorStepSize = QtCore.pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        self.motorsList = []
        self.fixedMotors = []
        self.motors = {}
        self.expOpts = {}
        self.logger = auxygen.devices.logger.Logger('Pylatus')
        self.cryoTemps = {}
        self.blowerTemps = {}
        self.lakeshoreTemps = {}
        self.monitorValues = {}
        self.running = False
        self.process = None
        self.phiMaxVelocity = 10
        self.prphiMaxVelocity = 10
        self.omegaMaxVelocity = 10
        self.maxVelocity = 10
        self.minPlvert = -20
        self.energy = 0
        self.noBeamCounts = 10
        self.wavelength = 0
        self.makePause = False
        self.scanType = 'Omega'
        self.paused = False
        self.oldFilter = None
        self.lakeshoreSensor = 'A'
        self.createDevices()

    def setMakePause(self, checked):
        self.makePause = checked

    def connectSignals(self):
        self.fileman.sigProcessFinished.connect(self.filemanProcessDone)
        self.sigFeedFileman.connect(self.fileman.feedCbfValues)
        self.sigStopFileman.connect(self.fileman.stop)
        self.pilatus.sigScanStepReady.connect(self.scanman.moveMotor)
        self.scanman.sigError.connect(self.logger.error)
        self.scanman.sigMoveMotor.connect(self.moveMotorAndWait)
        self.scanman.sigStopScan.connect(self.stopScan)
        self.scanman.sigShot.connect(self.pilatus.scanShot)
        self.sigMotorMoved.connect(self.scanman.updateMotorPosition)
        self.pilatus.sigExperimentFinished.connect(self.experimentFinishedByPilatus)
        self.cryo.sigStatus.connect(self.addCryostramTemperature)
        self.cryo.sigError.connect(self.logger.error)
        self.blower.sigTemperature.connect(self.addBlowerTemperature)
        self.blower.sigError.connect(self.logger.error)
        self.blower.sigConnected.connect(lambda: self.logger.info('Blower is connected'))
        self.lakeshore.sigTemperature.connect(self.addLakeshoreTemperature)
        self.monitor.sigValue.connect(self.monitorValueReceived)
        self.monitor.sigError.connect(self.logger.error)
        self.monitor.sigConnected.connect(lambda _: self.logger.info(f'Monitor {_} is connected'))
        self.sigExperimentResumed.connect(self.blower.resume)
        self.sigExperimentPaused.connect(self.blower.pause)
        self.sigExperimentPaused.connect(self.cryo.pause)
        self.sigExperimentResumed.connect(self.cryo.resume)
        self.pilatus.sigError.connect(self.logger.error)
        self.lakeshore.sigError.connect(self.logger.error)
        self.sigWavelength.connect(lambda w, e: self.pilatus.setEnergy(e))
        self.musst.sigIdle.connect(self.musstIsIdle)
        self.fileman.sigDirError.connect(self.logger.error)
        self.fileman.sigFileError.connect(self.logger.error)

    def createDevices(self):
        self.fileman = fileman.FileManager()
        self.musst = musst.Musst()
        self.pilatus = pilatus.Pilatus()
        self.scanman = scanman.ScanManager()
        self.cryo = auxygen.devices.cryostream.Cryostream()
        self.blower = auxygen.devices.blower.Blower()
        self.lakeshore = auxygen.devices.lakeshore.Lakeshore()
        self.monitor = monitor.Monitor()

    def monitorValueReceived(self, monValue):
        self.monitorValues[time.time()] = monValue
        noCounts = monValue < int(self.noBeamCounts * self.expOpts['expPeriod'])
        self.sigNoMonitorCounts.emit(noCounts)
        self.pauseExperiment(noCounts)

    def pauseExperiment(self, noCounts):
        if not self.makePause:
            return
        if noCounts and not self.paused:
            self.paused = True
            self.logger.error('!There is no beam! We abort the current data collection and wait until the beam gets '
                              'back')
            self.stopAllMotors()
            self.musst.abort()
            self.pilatus.abort()
            self.fileman.abort(self.process)
            self.process = None
            self.sigExperimentPaused.emit()
        elif self.paused and not noCounts:
            self.paused = False
            self.logger.info('The beam has come back. The last data collection is being restarted'
                             '\nIt is recommended to perform the general scan after')
            self.sigExperimentResumed.emit()
            self.period -= 1
            self.startNextPeriod()

    def experimentFinishedByPilatus(self):
        if not self.musst.isConnected():
            self.musstIsIdle()

    def musstIsIdle(self):
        if not self.paused and self.running and not self.scanman.running:
            data = self.cryoTemps, self.blowerTemps, self.monitorValues, self.lakeshoreTemps
            self.sigFeedFileman.emit(self.process, data)
            self.startNextPeriod()

    def startNextPeriod(self):
        if not self.expOpts:
            return
        self.setCurrentPeriod()
        self.runCurrentScan()
        if self.stopped:
            self.stopExperiment()

    @staticmethod
    def gcTemps(current, old):
        for timestamp in old:
            if timestamp in current:
                del current[timestamp]

    def filemanProcessDone(self, data, dirr, period):
        self.logger.info(f'-->The headers for period {period} in {dirr} have been written<--')
        self.cleanTemperatures(data)

    def cleanTemperatures(self, old):
        current = self.cryoTemps, self.blowerTemps, self.monitorValues, self.lakeshoreTemps
        for c, o in zip(current, old):
            self.gcTemps(c, o)

    def setMotors(self, motors):
        self.motorsList = motors

    def connectMotors(self):
        for motor in self.motorsList:
            self.connectGUIMotor(motor)

    def updateMotorViews(self):
        for m in self.motors:
            motor = self.motors[m]
            self.sigMotorMoved.emit(motor.name(), motor.position())

    def connectGUIMotor(self, motor):
        host, session, name = motor.split('->')
        self.connectMotor(host, session, name)

    def connectMotor(self, host, session, name):
        if name in self.motors:
            del self.motors[name]
        address = host, session
        motor = aspic.QMotor(address, name)
        motor.sigConnected.connect(lambda _: self.logger.info(f'Motor {_} has been connected'))
        motor.sigError.connect(self.logger.error)
        motor.sigLimitHit.connect(lambda _: self.logger.error(f'Motor {_} has hit the limit'))
        motor.sigNewPosition.connect(self.updateMotorPosition)
        motor.sigDisconnected.connect(lambda _: self.logger.warn(f'Motor {_} has been disconnected'))
        motor.sigStepSize.connect(self.sigMotorStepSize.emit)
        self.motors[name] = motor

    def updateMotorPosition(self, name, position):
        if name == Config.Mono:
            self.wavelength = utils.wavelength(position)
            self.energy = utils.energy(position)
            self.sigWavelength.emit(self.wavelength, self.energy)
        self.sigMotorMoved.emit(name, position)

    def setConfig(self):
        self.noBeamCounts = int(Config.NoBeamCounts)
        self.beamstopOn = float(Config.BeamstopOn)
        self.beamstopOff = float(Config.BeamstopOff)

    @auxygen.utils.split_motor_name
    def deleteMotor(self, name):
        if name in self.motors:
            del self.motors[name]

    def getMotor(self, name):
        if isinstance(name, aspic.QMotor):
            return name
        elif name and name in self.motors and self.motors[name].isConnected():
            return self.motors[name]
        else:
            self.logger.warning(f'The motor {name} is not connected. Skipped.')

    def getMotors(self, names):
        for name in names:
            yield self.getMotor(name)

    def setScanMotor(self, name):
        self.scanMotor = self.getMotor(name)
        if self.scanMotor:
            self.scanMotor.setDesiredPosition(self.expOpts['startAngle'])
        else:
            self.logger.error(f'Motor {name} is not connected. Skip it.')

    def preparePhiScan(self):
        self.setScanMotor(Config.Phi)
        if self.stopped or self.paused:
            return
        self.maxVelocity = self.phiMaxVelocity
        self.expOpts['oscAxis'] = 'PHI'
        motors = Config.Omega, Config.Kappa
        positions = self.expOpts['omegaphi'], self.expOpts['kappa']
        self.setFixedMotors(motors, positions)

    def prepareOmegaScan(self):
        self.setScanMotor(Config.Omega)
        if self.stopped or self.paused:
            return
        self.maxVelocity = self.omegaMaxVelocity
        self.expOpts['oscAxis'] = 'OMEGA'
        motors = Config.Phi, Config.Kappa
        positions = self.expOpts['omegaphi'], self.expOpts['kappa']
        self.setFixedMotors(motors, positions)

    def preparePrphiScan(self):
        self.setScanMotor(Config.Prphi)
        if self.stopped or self.paused:
            return
        self.expOpts['omegaphi'] = 0
        self.expOpts['kappa'] = 0
        self.expOpts['oscAxis'] = 'OMEGA'
        self.maxVelocity = self.prphiMaxVelocity

    def getAllMovingMotors(self):
        motors = []
        for name in self.motors:
            motor = self.motors[name]
            if motor.isConnected() and motor.state() in (motor.StateMoveStarted, motor.StateMoving):
                motors.append(motor)
        return motors

    def waitForMotorsMovement(self, motors=None):
        if not motors:
            motors = self.getAllMovingMotors()
        while motors:
            for motor in motors[:]:
                if self.stopped:
                    return
                if self.hasMotorReachedPosition(motor):
                    motors.remove(motor)
            GUtils.delay(100)

    def hasMotorReachedPosition(self, motor):
        if motor.state() == motor.StateReady:
            if motor.isOnLimit():
                self.logger.error(f'Motor {motor.name()} is at the limit switch! Continue at the current position!')
                self.sigMotorMoved.emit(motor.name(), motor.position())
                return True
            elif abs(motor.position() - motor.desiredPosition()) <= 1e-2:  # it seems that spec cannot do better
                self.sigMotorMoved.emit(motor.name(), motor.position())
                return True
            else:
                motor.move(motor.desiredPosition())
        return False

    def waitForMotorsMovementFromScript(self):
        if self.running:
            return
        self.running = True
        self.waitForMotorsMovement()
        self.running = False
        self.sigAllMotorsStopped.emit()

    def setMaxVelocity(self):
        for motorName, maxVelocity in zip((Config.Prphi, Config.Phi, Config.Omega),
                                          (self.prphiMaxVelocity, self.phiMaxVelocity, self.omegaMaxVelocity)):
            motor = self.getMotor(motorName)
            if motor and motor.isConnected():
                slew_rate = motor.stepSize() * maxVelocity
                if slew_rate != motor.slewRate():
                    motor.setSlewRate(slew_rate)
                    self.logger.info(f'slew_rate for motor {motor.name()} is set to {slew_rate}')

    def reconnectMotors(self):
        for motorName in self.motors:
            self.motors[motorName] = self.reconnectMotor(self.motors[motorName])
        self.musst.reset()
        self.connectMonitor()

    def stopAllMotors(self):
        self.logger.warn('Stopping all moving motors!')
        for motor in self.motors:
            self.motors[motor].stop()

    def stopMotor(self, name):
        motor = self.getMotor(name)
        if motor:
            self.logger.warn(f'Stop motor {name}')
            motor.stop()

    def startExperiment(self, opts):
        if self.running:
            self.logger.error('Stop the current measurements first!')
            return
        self.running = True
        self.expOpts = opts
        self.period = 0
        self.monitor.run(self.expOpts['expPeriod'])
        self.sigExperimentStarted.emit()
        self.initFixedMotors()
        self.setCurrentPeriod()
        self.runCurrentScan()
        if self.paused:
            self.sigExperimentPaused.emit()
        if self.stopped:
            self.stopExperiment()

    def runCurrentScan(self):
        if self.stopped or self.paused:
            return
        self.setCurrentScan()
        self.moveMotorsToStartPosition()
        self.setScanMotorVelocity()
        self.prepareDetector()
        self.fire()

    def setCurrentScan(self):
        if self.stopped or self.paused:
            return
        if self.scanType == 'Phi':
            self.preparePhiScan()
        elif self.scanType == 'Omega':
            self.prepareOmegaScan()
        elif self.scanType == 'Prphi':
            self.preparePrphiScan()
        else:
            self.logger.error('Something wrong with the scan definition. Stopping now.')
            self.running = False

    def setCurrentPeriod(self):
        if self.paused:
            return
        if self.running and self.period < self.expOpts['periods']:
            self.period += 1
            self.expOpts['period'] = self.period
            self.logger.info(f"Starting period {self.period:d} from {self.expOpts['periods']:d}.")
        else:
            self.running = False

    def stopExperiment(self):
        self.running = False
        self.monitor.abort()
        self.setMaxVelocity()
        self.sigExperimentFinished.emit()
        self.logger.info('The data collection has been finished.')

    def setScanMotorVelocity(self):
        if self.stopped or self.paused or not self.scanMotor:
            return
        step_size = self.scanMotor.stepSize()
        velocity = step_size * self.expOpts['step'] / self.expOpts['expPeriod']
        if velocity > step_size * self.maxVelocity:
            self.logger.error(f'Speed for {self.scanMotor.name()} is to high! Change exposure period. Stopping now.')
            self.running = False
            return
        self.logger.info(f'slew_rate for motor {self.scanMotor.name()} is set to {velocity}')
        self.scanMotor.setSlewRate(velocity)

    def prepareDetector(self):
        if self.stopped or self.paused:
            return
        if not self.pilatus.isConnected():
            self.logger.error('Detector is not connected. Check the camserver.')
            self.running = False
            return
        if self.expOpts['nop']:
            self.expOpts['cbfName'] = f'{self.expOpts["cbfBaseName"]}.cbf'
        else:
            self.expOpts['cbfName'] = f'{self.expOpts["cbfBaseName"]}_{self.period:04d}p.cbf'
        ms = Config.Plvert, Config.Pldistd, Config.Pldistf
        v, dd, df = list(m.position() if m else 0 for m in self.getMotors(ms))
        beamx = self.expOpts['beamX'] - v / self.expOpts['pixelX'] * 1e3
        dist = (self.expOpts['zeroDistance'] + df + dd) * 1e-3
        detSettings = (f'Detector_distance {dist:.3f} Detector_Voffset {v * 1e-3:.3f} Wavelength {self.wavelength:.5f} '
                       f'Beam_x {beamx:.3f} Beam_y {self.expOpts["beamY"]:.3f}')
        self.pilatus.initExperiment(self.expOpts['expPeriod'], self.expOpts['nframes'], detSettings)

    def fire(self):
        if self.stopped or self.paused:
            return
        o = self.expOpts
        self.process = self.fileman.startNewProcess(o)
        if not self.process:
            self.stopped = True
            return
        if o['step'] and self.scanMotor:
            finalPosition = self.scanMotor.position() + o['step'] * o['nframes']
            while self.scanMotor.state() == self.scanMotor.StateReady:
                GUtils.delay(100)
                if self.stopped:
                    return
                self.scanMotor.move(finalPosition)
                self.logger.info(f'Motor {self.scanMotor.name()} has been sent to {finalPosition:.5f}')
        self.musst.runScan(o['step'], o['nframes'], o['expPeriod'], o['mod'], o['mod2'])
        if self.musst.isConnected():
            self.pilatus.exposure(o['cbfName'])
        else:
            self.pilatus.shot(o['cbfName'])

    def moveMotorsToStartPosition(self):
        self.logger.info('Moving motors to the start positions')
        self.setMaxVelocity()
        if self.scanMotor:
            self.fixedMotors.append(self.scanMotor)
        for motor in self.fixedMotors:
            motor.move(motor.desiredPosition())
        self.waitForMotorsMovement(self.fixedMotors)

    def setFixedMotors(self, motors, positions):
        for m, p in zip(motors, positions):
            motor = self.getMotor(m)
            if motor:
                motor.setDesiredPosition(p)
                self.fixedMotors.append(motor)

    def initFixedMotors(self):
        self.fixedMotors = []
        motors = Config.Pldistd, Config.Pldistf, Config.Plvert, Config.Plrot, Config.Bstop
        positions = (self.expOpts['pldistd'], self.expOpts['pldistf'], self.expOpts['plvert'], self.expOpts['plrot'],
                     float(Config.BeamstopOn))
        self.setFixedMotors(motors, positions)

    def setPrphiMaxVelocity(self, value):
        self.prphiMaxVelocity = value

    def setPhiMaxVelocity(self, value):
        self.phiMaxVelocity = value

    def setPhiScan(self):
        self.scanType = 'Phi'

    def setOmegaScan(self):
        self.scanType = 'Omega'

    def setPrphiScan(self):
        self.scanType = 'Prphi'

    def setOmegaMaxVelocity(self, value):
        self.omegaMaxVelocity = value

    def abortCurrentExperiment(self):
        self.paused = False
        self.stopAllMotors()
        self.pilatus.abort()
        self.musst.abort()
        self.fileman.abort(self.process)
        self.process = None

    def abortExperiment(self):
        if self.stopped:
            return
        self.abortCurrentExperiment()
        self.stopExperiment()

    def openShutter(self):
        self.musst.openShutter()

    def closeShutter(self):
        self.musst.closeShutter()

    def start(self):
        self.connectSpec()
        self.pilatus.connectDetector()
        self.pilatus.adjust(self.energy)
        self.fileman.clean(Config.DataDir)

    def connectSpec(self):
        self.connectMotors()
        self.musst.connectToSpec()
        self.monitor.connectToSpec()

    def stop(self):
        self.abortExperiment()
        self.abortScan()
        self.running = False
        self.pilatus.stop()
        self.monitor.abort()
        self.sigStopFileman.emit()
        self.cryo.stop()
        self.blower.stop()
        self.lakeshore.stop()

    def moveMotor(self, motor, position, maxVelocity=True):
        if maxVelocity:
            self.setMaxVelocity()
        motor = self.getMotor(motor)
        if motor:
            motor.move(position)
            self.logger.info(f'Move motor {motor.name()} from {motor.position():.5f} to {position:.5f}')
        return motor

    def moveMotorAndWait(self, motor, position):
        motor = self.moveMotor(motor, position)
        if not motor:
            return
        old, self.running = self.running, True
        self.waitForMotorsMovement([motor])
        self.running = old

    def moveMotorRelative(self, motorName, position, maxVelocity=True):
        if maxVelocity:
            self.setMaxVelocity()
        motor = self.getMotor(motorName)
        if motor:
            self.logger.info(f'Move {motor.name()} from {motor.position():.5f} to {motor.position() + position:.5f}')
            motor.moveRelative(position)

    def addLakeshoreTemperature(self, sensor, value):
        if self.running and sensor == self.lakeshoreSensor:
            self.lakeshoreTemps[time.time()] = value

    def addCryostramTemperature(self, status):
        if self.running:
            self.cryoTemps[time.time()] = status['SampleTemp']

    def addBlowerTemperature(self, temp):
        if self.running:
            self.blowerTemps[time.time()] = temp

    def runScan(self, params):
        if self.running:
            self.logger.error('Something is running, stop it before the scan!')
            return
        if not params:
            params = {'auto': True, 'axis': Config.ScanAxis, 'expPeriod': float(Config.ScanTime),
                      'nfilter': int(Config.ScanFilter)}
        axis, bstop, fltr = self.getMotors((params['axis'], Config.Bstop, Config.Filter))
        if not axis:
            self.logger.error(f'The scanning axis {params["axis"]} is not connected! Stopping')
            return
        if params['auto'] and not bstop:
            self.logger.error(f'The beamstop motor {Config.Bstop} is not connected! Stopping')
            return
        if params['auto'] and not fltr:
            self.logger.error(f'The filter motor {Config.Filter} is not connected! Stopping')
            return
        self.running = True
        if fltr:
            self.oldFilter = fltr.position()
            self.moveMotor(fltr, params['nfilter'])
            self.waitForMotorsMovement([fltr])
        params['backup'] = axis.position()
        if self.stopped:
            return
        if params['auto']:
            self.moveMotor(bstop, self.beamstopOff)
            self.waitForMotorsMovement([bstop])
            if self.stopped:
                return
        self.pilatus.initExperiment(params['expPeriod'], 1)
        self.openShutter()
        self.scanman.run(params)

    def stopScan(self, auto):
        if self.stopped:
            return
        self.pilatus.scanShot()
        self.closeShutter()
        if auto:
            self.moveMotor(Config.Bstop, self.beamstopOn)
            self.waitForMotorsMovement()
            if self.oldFilter is not None:
                self.moveMotor(Config.Filter, self.oldFilter)
                self.oldFilter = None
        self.waitForMotorsMovement()
        self.running = False
        self.scanman.running = False

    def abortScan(self):
        if self.running:
            self.stopAllMotors()
            self.scanman.abortScan()

    def updateWavelength(self, value):
        mono = self.getMotor(Config.Mono)
        if mono:
            mono.setOffset(utils.angle(value) - mono.dialPosition())

    def setMinPlvert(self, value):
        self.minPlvert = value

    def setLakeshoreSensor(self, value):
        self.lakeshoreSensor = value

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, running):
        self._running = running

    @property
    def stopped(self):
        return not self._running

    @stopped.setter
    def stopped(self, stopped):
        self._running = not stopped
