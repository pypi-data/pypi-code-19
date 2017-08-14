#!/usr/bin/env python
# starfeeder/task.py

"""
    Copyright (C) 2015-2017 Rudolf Cardinal (rudolf@pobox.com).

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import logging
import re
from typing import List, Optional

import arrow
from cardinal_pythonlib.regexfunc import CompiledRegexMemory
from whisker.qt import exit_on_exception
from whisker.qtclient import WhiskerTask
from whisker.sqlalchemy import get_database_engine  # session_thread_scope

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from sqlalchemy.orm import Session, sessionmaker
from starfeeder.models import (
    MassEvent,  # for type hints
    MassEventRecord,
    MasterConfig,
    RfidEvent,  # for type hints
    RfidEventRecord,
)
from starfeeder.settings import get_database_settings
from starfeeder.version import VERSION

log = logging.getLogger(__name__)


TARE_COMMAND_REGEX = re.compile(r"^Tare (\w+)$")  # e.g. "Tare balance0"

MASS_BROADCAST_EVENT_NAME = "MASS_EVENT"
BALANCE_UNLOCK_BROADCAST_EVENT_NAME = "BALANCE_UNLOCK_EVENT"
RFID_BROADCAST_EVENT_NAME = "RFID_EVENT"

DATABASE_FLUSH_PERIOD_SEC = 30


class WeightWhiskerTask(WhiskerTask):  # Whisker thread B
    """Doesn't define an end, deliberately."""

    # =========================================================================
    # Extra signals
    # =========================================================================

    tare_requested = pyqtSignal(str)

    # =========================================================================
    # Constructor
    # =========================================================================

    def __init__(self, wcm_prefix: str = "", parent: QObject = None,
                 name: str = "whisker_task", **kwargs) -> None:
        super().__init__(parent=parent, name=name, **kwargs)
        self.wcm_prefix = wcm_prefix
        self.dbsettings = get_database_settings()
        self.rfid_effective_time_s = None
        self.session = None  # type: Session
        self.rfid_records = []  # type: List[RfidEventRecord]
        self.mass_records = []  # type: List[MassEventRecord]
        self.running = False

    # =========================================================================
    # Thread management
    # =========================================================================

    @pyqtSlot()
    def thread_started(self) -> None:
        engine = get_database_engine(self.dbsettings, pool_pre_ping=True)
        session_factory = sessionmaker(bind=engine)
        # ... uses defaults of autoflush=True, autocommit=False
        self.session = session_factory()
        # with session_thread_scope(self.dbsettings) as session:
        config = MasterConfig.get_singleton(self.session)
        self.rfid_effective_time_s = config.rfid_effective_time_s
        self.running = True

    @pyqtSlot()
    def stop(self) -> None:
        self.info("WeightWhiskerTask: stopping")
        self.flush_rfid_records()
        self.flush_mass_records()
        self.session.close()
        self.running = False
        super().stop()

    # =========================================================================
    # Whisker events/comms
    # =========================================================================

    @pyqtSlot()
    @exit_on_exception
    def on_connect(self) -> None:
        # self.debug("DERIVED on_connect")
        # debug_object(self)
        # self.whisker.command("TimerSetEvent 2000 5 bop")
        self.whisker.report_name("Starfeeder {}".format(VERSION))
        self.whisker.permit_client_messages(True)

    @pyqtSlot(str, arrow.Arrow, int)
    @exit_on_exception
    def on_event(self, event: str, timestamp: arrow.Arrow,
                 whisker_timestamp_ms: int) -> None:
        pass
        # if event == "bop":
        #     self.status("boop")

    # noinspection PyUnusedLocal
    @pyqtSlot(int, str, arrow.Arrow, int)
    @exit_on_exception
    def on_client_message(self,
                          source_client_num: int,
                          client_msg: str,
                          timestamp: arrow.Arrow,
                          whisker_timestamp_ms: int) -> None:
        gre = CompiledRegexMemory()
        if gre.match(TARE_COMMAND_REGEX, client_msg):
            balance_name = gre.group(1)
            self.info("Whisker client {} asks to tare balance "
                      "{}".format(source_client_num, repr(balance_name)))
            self.tare_requested.emit(balance_name)
        else:
            self.debug("Ignoring message from Whisker client {}: {}".format(
                source_client_num, repr(client_msg)))
            # Note that a whole bunch of irrelevant client messages might come
            # here. Ignore any others.

    def broadcast(self, msg: str) -> None:
        if not self.whisker.is_connected():
            return
        if self.wcm_prefix:
            msg = "{}{}".format(self.wcm_prefix, msg)
        self.whisker.broadcast(msg)

    # =========================================================================
    # Other events
    # =========================================================================

    def tick(self) -> None:
        if self.running:
            self.flush_rfid_records()
            self.flush_mass_records()

    # =========================================================================
    # RFID handling
    # =========================================================================

    def ongoing_rfid_record(self, rfid_event: RfidEvent) \
            -> Optional[RfidEventRecord]:
        now = rfid_event.timestamp
        for e in self.rfid_records:
            if (e.reader_id == rfid_event.reader_id and
                    e.rfid == rfid_event.rfid and
                    e.active(now, self.rfid_effective_time_s)):
                return e
        return None

    def flush_rfid_records(self) -> None:
        if not self.running:
            self.error("Not running: ignoring call to flush_rfid_records()")
            return
        self.debug("Flushing RFID events to database")
        self.session.commit()
        now = arrow.now()
        self.rfid_records = [e for e in self.rfid_records
                             if e.active(now, self.rfid_effective_time_s)]

    def record_rfid_detection(self, rfid_event: RfidEvent):
        if not self.running:
            self.error("Not running: ignoring call to record_rfid_detection()")
            return
        now = rfid_event.timestamp
        record = self.ongoing_rfid_record(rfid_event)
        if record:
            record.last_detected_at = now
            record.n_events += 1
        else:
            record = RfidEventRecord(
                reader_id=rfid_event.reader_id,
                rfid=rfid_event.rfid,
                first_detected_at=now,
                last_detected_at=now,
                n_events=1,
            )
            self.rfid_records.append(record)
            self.session.add(record)
            # DO NOT COMMIT, for speed

    @pyqtSlot(RfidEvent)
    @exit_on_exception
    def on_rfid(self, rfid_event: RfidEvent) -> None:
        """
        Record an RFID event.

        Since this task runs in a non-GUI thread, it's a good place to do the
        main RFID processing.

        Only one thread should be writing to the database, to avoid locks.

        Don't hold the session too long, on general principles.
        """
        if not isinstance(rfid_event, RfidEvent):
            self.critical("Bad rfid_event: {}".format(rfid_event))
            return
        self.record_rfid_detection(rfid_event)
        # self.status("RFID received: {}".format(rfid_event))
        self.broadcast(
            "{event_name}: reader {reader}, RFID {rfid}, "
            "timestamp {timestamp}".format(
                event_name=RFID_BROADCAST_EVENT_NAME,
                rfid=rfid_event.rfid,
                reader=rfid_event.reader_name,
                timestamp=rfid_event.timestamp,
            )
        )

    # =========================================================================
    # Mass handling
    # =========================================================================

    def ongoing_mass_record(self, mass_event: MassEvent) -> \
            Optional[MassEventRecord]:
        # Don't match on RFID, because an "RFID + lock" event can be
        # followed by a matching "no RFID + unlock" event.
        # For the same reason, ignore reader_id.
        for m in self.mass_records:
            if m.balance_id == mass_event.balance_id and not m.is_complete:
                return m
        return None

    def record_mass_detection(self, mass_event: MassEvent) -> None:
        if not self.running:
            self.error("Not running: ignoring call to record_mass_detection")
            return
        if mass_event.locked_now:
            mr = MassEventRecord(
                rfid=mass_event.rfid,
                reader_id=mass_event.reader_id,
                balance_id=mass_event.balance_id,
                at=mass_event.timestamp,
                mass_kg=mass_event.mass_kg,
            )
            self.mass_records.append(mr)
            self.session.add(mr)
        elif mass_event.unlocked_now:
            mr = self.ongoing_mass_record(mass_event)
            if mr:
                mr.record_unlock(mass_event)
            else:
                self.warning("Mass unlock event without a matching lock event")
        # No commit at this point, for speed

    def flush_mass_records(self) -> None:
        if not self.running:
            self.error("Not running: ignoring call to flush_mass_records()")
            return
        self.debug("Flushing mass events to database")
        self.session.commit()
        self.mass_records = [m for m in self.mass_records
                             if not m.is_complete]

    @pyqtSlot(MassEvent)
    @exit_on_exception
    def on_mass(self, mass_event: MassEvent) -> None:
        """
        Receive a mass event. Ask the MassIdentifiedEvent class to work out if
        it represents an identified mass event (and store it, if so).
        Broadcast the information to the Whisker client.
        """
        if not isinstance(mass_event, MassEvent):
            self.critical("Bad mass_event: {}".format(mass_event))
            return
        if not ((mass_event.locked_now and mass_event.rfid is not None) or
                mass_event.unlocked_now):
            return
        self.record_mass_detection(mass_event)
        self.broadcast(
            "{event_name}: reader {reader}, RFID {rfid}, balance {balance}, "
            "mass {mass_kg} kg, timestamp {timestamp}".format(
                event_name=(MASS_BROADCAST_EVENT_NAME if mass_event.locked_now
                            else BALANCE_UNLOCK_BROADCAST_EVENT_NAME),
                reader=mass_event.reader_name,
                rfid=mass_event.rfid,
                balance=mass_event.balance_name,
                mass_kg=mass_event.mass_kg,
                timestamp=mass_event.timestamp,
            )
        )
