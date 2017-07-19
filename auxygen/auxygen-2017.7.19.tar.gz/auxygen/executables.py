#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets


def cryostream():
    from .devices.cryostream import Cryostream
    from .gui.wcryo import WCryo
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    cryo = Cryostream()
    wcryo = WCryo(None)
    wcryo.sigRestart.connect(cryo.restart)
    wcryo.sigStop.connect(cryo.cstop)
    wcryo.sigPause.connect(cryo.pause)
    wcryo.sigResume.connect(cryo.resume)
    wcryo.sigTurboOn.connect(cryo.turboOn)
    wcryo.sigTurboOff.connect(cryo.turboOff)
    wcryo.sigCool.connect(cryo.cool)
    wcryo.sigRamp.connect(cryo.ramp)
    wcryo.sigPlat.connect(cryo.plat)
    wcryo.sigHold.connect(cryo.hold)
    wcryo.sigEnd.connect(cryo.end)
    wcryo.sigPurge.connect(cryo.purge)
    wcryo.sigConnect.connect(cryo.start)
    wcryo.sigDisconnect.connect(cryo.stop)
    cryo.sigError.connect(wcryo.cryoError)
    cryo.sigStatus.connect(wcryo.updateStatus)
    wcryo.show()
    sys.exit(app.exec_())


def blower():
    import sys
    from .devices.blower import Blower
    from .gui.wblower import WBlower
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    dblower = Blower()
    dblower.logger.logger.sigPostLogMessage.connect(lambda _: print(_.strip()))
    wblower = WBlower(None)
    dblower.sigTemperature.connect(wblower.updateTemperature)
    dblower.sigConnected.connect(wblower.connectionSucceed)
    dblower.sigError.connect(wblower.connectionFailed)
    wblower.sigConnect.connect(dblower.connectToSpec)
    wblower.sigDisconnect.connect(dblower.stop)
    wblower.sigRun.connect(dblower.run)
    wblower.show()
    sys.exit(app.exec_())


def wscripted():
    from .gui.wscripted import WScriptEd
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    ww = WScriptEd(None, {})
    ww.show()
    sys.exit(app.exec_())


def wseq():
    from .gui.wseq import WSeq
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    ww = WSeq(None)
    ww.show()
    sys.exit(app.exec_())


def lakeshore():
    from .devices.lakeshore import Lakeshore
    from .gui.wlakeshore import WLakeshore
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    dlakeshore = Lakeshore()
    wwlakeshore = WLakeshore(None)
    wwlakeshore.sigConnect.connect(dlakeshore.start)
    wwlakeshore.sigDisconnect.connect(dlakeshore.stop)
    wwlakeshore.sigSetPoint.connect(dlakeshore.setSetP)
    wwlakeshore.sigSetManual.connect(dlakeshore.setMout)
    wwlakeshore.sigSetPID.connect(dlakeshore.setPID)
    wwlakeshore.sigSetRange.connect(dlakeshore.setRange)
    wwlakeshore.sigReadOutput.connect(dlakeshore.setReadOutputAndSensor)
    wwlakeshore.sigReadSensor.connect(dlakeshore.setReadOutputAndSensor)
    dlakeshore.sigError.connect(wwlakeshore.lakeshoreError)
    dlakeshore.sigConnected.connect(wwlakeshore.connected)
    dlakeshore.sigDisconnected.connect(wwlakeshore.disconnected)
    dlakeshore.sigTemperature.connect(wwlakeshore.updateTemperature)
    dlakeshore.sigHeater.connect(wwlakeshore.updateHeater)
    dlakeshore.sigRange.connect(wwlakeshore.updateRange)
    dlakeshore.sigPID.connect(wwlakeshore.updatePID)
    dlakeshore.sigSetpoint.connect(wwlakeshore.updateSetpoint)
    wwlakeshore.loadSettings()
    wwlakeshore.show()
    sys.exit(app.exec_())
