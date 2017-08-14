"""HDF5 support for Gymbag OpenAI Gym data recorder."""

# Copyright (C) 2017  Doctor J
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import atexit
import json
import warnings
from typing import Union, Tuple, Optional, Dict, Any, Iterable

import gym
import numpy as np
import tables

from .core import Recorder, TObs, TAct, getshape, serialize_space, TIME, OBS, ACTION, REWARD, DONE, INFO, JSON_COMPACT_SEPARATORS, RecordEnv, Reader, deserialize_space, TData, set_done


MAX_ATTRIBUTE_SIZE = 64 * 1024      # PyTables has some unfortunate limits


def record_hdf5(env: gym.Env, filename: str, description: str = '') -> RecordEnv[TObs, TAct]:
    """Wrap an `env` and record its data to an HDF5 file.

    Data is recorded to table with the same name as the environment (spec), or the `env` class name if `env` has no spec.

    :param description: Human-readable string that goes in the HDF5 table metadata so you can remember where this data came from later.
    """
    table_name = env.spec.id if hasattr(env, 'spec') else env.__class__.__name__
    recorder = HDF5Recorder[TObs, TAct](filename, env.observation_space, env.action_space, table_name, description)
    return RecordEnv[TObs, TAct](env, recorder)


class HDF5Recorder(Recorder[TObs, TAct]):
    """Record to HDF5 independent of an environment (e.g. for saving test data).

    Data is saved at the root node unless `table_name` is a path.
    Data is saved to a table named `table_name` if given, else the filename is used as the table name.
    Will set the last `done` value to True before a reset or close, even if passed ``done == False``.
    Observations and actions are always stored as floats (Discrete spaces are converted to int by the Reader).
    All floats are stored as 32-bit.  Tables are compressed with blosc:zstd (or zlib if unavailable).
    """
    # A Pandas DataFrame column can't contain multi-dimensional arrays (like observations and actions), otherwise we'd totally use Pandas format.
    # The format relies on seeing done = True to delimit episodes
    # So, reset() and close() need to ensure done = True on the *previous* step, even if it had done = False
    # So, we always buffer at least the last row, so we can set done = True before writing.  Also helps with performance.
    # (Had tried writing immediately, then read/modify/write if done changed, but it was slow.)
    # pylint: disable=too-many-arguments
    def __init__(self, filename: str, observation_space: Union[gym.Space, Tuple[int, ...]], action_space: Union[gym.Space, Tuple[int, ...]], table_name: str = '', description: str = '', max_info_bytes: int = 1024) -> None:
        """:param max_info_bytes: info dicts are encoded as JSON strings, and PyTables only supports fixed-length strings,
          so you gotta choose an upper bound.  If you set this to 0, info will not be stored.
        :param observation_space: If you pass a :class:`gym.Space`, it will be stored in the table metadata for use by the reader.
        :param action_space: If you pass a :class:`gym.Space`, it will be stored in the table metadata for use the by reader.
        """
        self._max_info_bytes = max_info_bytes
        observation_shape, obs_desc = observation_space, None
        if isinstance(observation_space, gym.Space):
            observation_shape = getshape(observation_space)
            obs_desc = serialize_space(observation_space)
            if len(obs_desc) > MAX_ATTRIBUTE_SIZE:
                warnings.warn('Space {} encodes to {} bytes, which may not fit PyTables HDF5 metadata limits.'.format(observation_space, len(obs_desc)))

        action_shape, act_desc = action_space, None
        if isinstance(action_space, gym.Space):
            action_shape = getshape(action_space)
            act_desc = serialize_space(action_space)
            if len(act_desc) > MAX_ATTRIBUTE_SIZE:
                warnings.warn('Space {} encodes to {} bytes, which may not fit PyTables HDF5 metadata limits.'.format(action_space, len(act_desc)))

        # TODO: We should think about storing Discrete spaces as int columns, so we don't have to convert them on reading.
        class Step(tables.IsDescription):
            """Schema definition for HDF5 format."""
            # pylint: disable=too-few-public-methods
            time = tables.Time64Col(pos=TIME)
            observation = tables.Float32Col(shape=observation_shape, pos=OBS)
            action = tables.Float32Col(shape=action_shape, pos=ACTION)
            reward = tables.Float32Col(pos=REWARD)
            done = tables.BoolCol(pos=DONE)
            info = tables.StringCol(max_info_bytes, pos=INFO)

        self._h5file = tables.open_file(filename, mode='a', title='OpenAI Gym Gymbag Data', filters=tables.Filters(complevel=2, complib='blosc:zstd'))       # zstd@2 compresses Breakout-v0 better than zlib@7 but twice as fast
        table_name = table_name or 'Gym-Environment-Data'
        try:
            self._h5table = self._h5file.get_node('/', table_name)
        except tables.NoSuchNodeError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", tables.NaturalNameWarning)
                self._h5table = self._h5file.create_table('/', table_name, Step, description)     # That's a human-readable description, not the HDF5 notion
                self._h5table.attrs.gymbag_format = 1
                self._h5table.attrs.observation_space = obs_desc
                self._h5table.attrs.action_space = act_desc
        self._buffer = []
        self._bufsiz = 16
        assert self._bufsiz >= 2            # We keep 1 row around until we know whether or not the next step has done = True
        atexit.register(self.__del__)       # In case you forget to close the env, avoids message from PyTables

    def on_reset(self, unix_time: float, observation: TObs, action: TAct, reward: float = np.nan, done: bool = False, info: Optional[Dict[Any, Any]] = None) -> None:
        """Start a new episode."""
        if self._buffer:
            self._buffer[-1] = set_done(self._buffer[-1])       # Agent may have quit before env said 'done', but we still want to demarcate episodes.
        self.on_step(unix_time, observation, action, reward, done, info)

    def on_step(self, unix_time: float, observation: TObs, action: TAct, reward: float, done: bool, info: Optional[Dict[Any, Any]]) -> None:
        """Record step data.  Note that `observation` is the one that comes *before* the action and reward."""
        row = (
            unix_time,
            observation,
            action,
            reward,
            done,
            b'' if not info or self._max_info_bytes == 0 else json.dumps(info, separators=JSON_COMPACT_SEPARATORS, sort_keys=True).encode('ascii')
        )
        self._buffer.append(row)

        if len(self._buffer) >= self._bufsiz:
            self._h5table.append(self._buffer[:-1])         # Don't write last because we don't know if 'done' will change until next step
            self._buffer = self._buffer[-1:]

    def on_close(self) -> None:
        """Close the underlying HDF5 file."""
        if hasattr(self, '_h5file') and self._h5file.isopen:      # Guard against multiple closes
            if self._buffer:
                self._buffer[-1] = set_done(self._buffer[-1])       # Agent may have quit before env said 'done', but we still want to demarcate episodes.
                self._h5table.append(self._buffer)
                self._buffer = []

            self._h5file.close()

    def __del__(self):
        self.on_close()


class HDF5Reader(Reader[TObs, TAct]):
    """Iterate over gym data recorded in HDF5."""
    #pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self, filename: str, table: Optional[str] = None) -> None:
        """:Return: an iterable of episodes of step data read from HDF5 `filename`.

        Each step is a tuple of ``(time, observation, action, reward, done, info)``.
        The first step in an episode will have `NaN` action and reward.
        The last step in an episode will have ``done == True``.
        Observations and actions are stored as floats, but converted to int if the corresponding
        space is Discrete.
        """
        super().__init__()
        self._h5file = tables.open_file(filename, 'r')
        nodes = self._h5file.list_nodes(table or '/')
        if len(nodes) != 1:
            raise ValueError('Did not find exactly one table: {}'.format(', '.join(node._v_name for node in nodes)))        # pylint: disable=protected-access
        self._h5table = nodes[0]
        self._rows = None
        self.name = self._h5table.name          #: The environment name
        self.nsteps = self._h5table.nrows       #: The total number of steps (in all episodes) in this Reader.
        self.description = self._h5table.title  #: The human-readable description
        self.observation_space = None           #: The observation space
        self.action_space = None                #: The action space
        try:
            self.observation_space = deserialize_space(getattr(self._h5table.attrs, 'observation_space', None))
            self.action_space = deserialize_space(getattr(self._h5table.attrs, 'action_space', None))
        except Exception as exc:
            raise Warning('Unable to load environment space from file metadata') from exc

    def __iter__(self) -> Iterable[Iterable[TData[TObs, TAct]]]:
        self._rows = self._h5table.iterrows()
        return self

    def __next__(self) -> Iterable[Iterable[TData[TObs, TAct]]]:
        if self._rows.nrow < self._h5table.nrows - 1:
            return self._grouper()
        else:
            raise StopIteration()

    def _grouper(self) -> Iterable[TData[TObs, TAct]]:      # Avoid making closures in a loop
        """Generate one episode."""
        done = False
        first = True
        while not done:
            row = next(self._rows)        # Exit on StopIteration
            utime, obs, action, reward, done, info = (row[field] for field in ('time', 'observation', 'action', 'reward', 'done', 'info'))
            if first:
                first = False
                if not np.all(np.isnan(action) | (np.asarray(action) == 0)) or not np.isnan(reward):
                    warnings.warn('First step should not have action or reward: data may be corrupt.\n{}'.format((utime, obs, action, reward, done, info)))
            if isinstance(self.observation_space, gym.spaces.Discrete):
                obs = int(obs)
            if isinstance(self.action_space, gym.spaces.Discrete):
                action = int(action)
            info = json.loads(info.decode('ascii')) if info else None
            yield utime, obs, action, reward, done, info

    def close(self) -> None:
        """Close the underlying HDF5 file."""
        if hasattr(self, '_h5file'):
            self._h5file.close()

    def __del__(self) -> None:
        self.close()
