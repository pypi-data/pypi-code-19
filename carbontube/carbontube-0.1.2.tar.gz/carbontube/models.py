# -*- coding: utf-8 -*-
# <carbontube - distributed pipeline framework>
#
# Copyright (C) <2016>  Gabriel Falcão <gabriel@nacaolivre.org>
# (C) Author: Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import pickle
import uuid


class Job(dict):
    # STATES (and ultimately queues)

    # [enqueued]
    # [running]
    # [succeeded]
    # [failed]
    @property
    def id(self):
        return self.get('id', None)

    @property
    def type(self):
        return self.get('job_type', None)

    @classmethod
    def from_dict(cls, data):
        if not data:
            msg = 'Job.from_dict requires a non-empty dict as argument, instead got: {0}'
            raise ValueError(msg.format(repr(data)))

        return cls(data)

    @classmethod
    def new(cls, job_type, instructions):
        data = {}
        data['id'] = str(uuid.uuid4())
        data['job_type'] = job_type
        data['instructions'] = instructions.get('instructions') or instructions
        return cls.from_dict(data)

    def __eq__(self, other):
        return pickle.dumps(self.to_dict()) == pickle.dumps(other.to_dict())

    def to_dict(self):
        return dict(self)


class Worker(dict):
    @property
    def id(self):
        return self.get('id', None)

    @property
    def job_type(self):
        return self.get('job_type', None)

    @property
    def phase_name(self):
        return self.get('phase_name', None)

    @property
    def address(self):
        return self.get('address', None)

    @classmethod
    def from_event(cls, event):
        return cls(event.data)

    def __hash__(self):
        return hash(self.id)
