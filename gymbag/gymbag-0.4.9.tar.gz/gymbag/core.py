"""
Simple, efficient OpenAI Gym environment recording and playback.
"""

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

import itertools
import json
import logging
import sys
from time import time
from typing import Callable, Union, Optional, Dict, Any, Tuple, Iterable, Generic, TypeVar, List
from abc import ABCMeta, abstractmethod

import numpy as np
import gym
import gym.spaces

#: Type of observations (discrete, box)
TObs = TypeVar('TObs', float, np.ndarray)       # pylint: disable=invalid-name
#: Type of actions (discrete, box)
TAct = TypeVar('TAct', float, np.ndarray)       # pylint: disable=invalid-name
#: Type returned by ``step()``: obs, reward, done, info
TStep = Tuple[TObs, float, bool, Optional[Dict[Any, Any]]]     # pylint: disable=invalid-name
#: Type of data data recorded at each step: time, obs, action, reward, done, info
TData = Tuple[float, TObs, TAct, float, bool, Optional[Dict[Any, Any]]]     # pylint: disable=invalid-name

TIME, OBS, ACTION, REWARD, DONE, INFO = range(6)        #: Data field indices
JSON_COMPACT_SEPARATORS = (',', ':')


class Recorder(Generic[TObs, TAct], metaclass=ABCMeta):
    """Abstract base class for Recorders.  Subclass to record to a particular format.

    In order to delineate episodes on read, it is important that the last step in an episode have ``done = True``.
    This may necessitate buffering a row if it cannot be modified after written.
    """
    # pylint: disable=too-many-arguments
    def on_reset(self, unix_time: float, observation: TObs, action: TAct, reward: float = np.nan, done: bool = False, info: Optional[Dict[Any, Any]] = None) -> None:
        """Default implementation calls :meth:`on_step`.

        Can ignore action, reward, done, info; they provide default values for fixed-column implementations that need to write something."""
        self.on_step(unix_time, observation, action, reward, done, info)

    @abstractmethod
    def on_step(self, unix_time: float, observation: TObs, action: TAct, reward: float, done: bool, info: Optional[Dict[Any, Any]]) -> None:
        """Record step data.  By default this is also called on reset with the first observation and `NaN` action and reward."""
        pass

    def on_close(self) -> None:
        """Close this Recorder."""
        pass


class RecordEnv(Generic[TObs, TAct], gym.Env):
    """Wrap a gym environment and pass its data to a :class:`Recorder` to record a specific format.

    Recorder callbacks are called after the corresponding environment call.
    Reset and step times are unix time UTC float epoch seconds after the corresponding environment call.
    """
    # pylint: disable=protected-access
    def __init__(self, env: gym.Env, recorder: Recorder[TObs, TAct]) -> None:
        self.env = env
        self.observation_space = env.observation_space
        self.action_space = env.action_space
        self.recorder = recorder

    def _reset(self) -> TObs:
        obs = self.env._reset()
        self.recorder.on_reset(time(), obs, null_sample(self.action_space), np.nan, False, None)
        return obs

    def _step(self, action: TAct) -> TStep[TObs]:
        obs, reward, done, info = self.env._step(action)        # type: TStep[TObs]
        self.recorder.on_step(time(), obs, action, reward, done, info)
        return obs, reward, done, info

    def _render(self, mode: str = 'human', close: bool = False) -> None:
        self.env._render(mode=mode, close=close)

    def _seed(self, seed=None) -> None:
        self.env._seed(seed)

    def _close(self) -> None:
        self.env._close()
        self.recorder.on_close()


class ListRecorder(Recorder[TObs, TAct]):
    """Record environment data to a list in memory.

    The list can be accessed with the ``.data`` attribute."""
    # pylint: disable=too-many-arguments
    def __init__(self) -> None:
        self._data = []

    def on_reset(self, unix_time: float, observation: TObs, action: TAct, reward: float = np.nan, done: bool = False, info: Optional[Dict[Any, Any]] = None) -> None:
        """Start a new episode."""
        self.data.append([])
        self.on_step(unix_time, observation, action, reward, done, info)

    def on_step(self, unix_time: float, observation: TObs, action: TAct, reward: float, done: bool, info: Optional[Dict[Any, Any]]) -> None:
        """Record step data."""
        if not self.data:
            raise ValueError('Must call reset() before step()')
        self.data[-1].append((unix_time, observation, action, reward, done, info))

    @property
    def data(self) -> List[List[TData[TObs, TAct]]]:
        """The list of recorded episodes."""
        return self._data


class Reader(Generic[TObs, TAct], metaclass=ABCMeta):
    """Abstract base class to iterate over recorded gym data as well as provide metadata like spaces and size."""
    # This is a class and not just an iterator so we can provide metadata like the obs and action spaces.
    # pylint: disable=too-few-public-methods
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.observation_space = None       #: The observation space
        self.action_space = None            #: The action space
        self.nsteps = None                  #: The total number of steps (in all episodes) in this Reader

    @abstractmethod
    def __iter__(self) -> Iterable[Iterable[TData[TObs, TAct]]]:
        """Iterate over the episodes stored in this Reader."""
        pass

    def close(self) -> None:
        """Close this Reader."""
        pass


class PlaybackEnv(Generic[TObs, TAct], gym.Env):
    """A gym environment that plays back a sequence of recorded observations, ignoring actions.

    End of playback can be detected by checking for ``env.played_out == True`` after each "done" step
    but before the next reset.
    """
    # pylint: disable=too-many-instance-attributes
    metadata = {'render.modes': ['human']}
    # TODO: Consider redesigning this with a next_episode() method instead of .played_out, like PlaybackAgent, or having reset() return None.

    def __init__(self, source: Union[Reader, Iterable[Iterable[TData]]], observation_space: Optional[gym.Space] = None, action_space: Optional[gym.Space] = None) -> None:      # pylint: disable=bad-whitespace
        """:param source: :class:`Reader` or :class:`Iterable` over episodes, each of which is an iterable over steps,
          each of which is a tuple of ``(time, obs, action, reward, done, info)``.
          The action and reward from the first item in each episode are discarded.
          Note :meth:`reset` returns the observation from the fist item in each episode iterable,
          while the first :meth:`step` returns the reward, done, and info from the second.
        :param observation_space: If given, override the ``observation_space`` attribute of the `source`.
        :param action_space: If given, override the ``action_space`` attribute of the `source`.
        """
        self._log = logging.getLogger(__name__)
        self._log.setLevel(logging.INFO)
        self._log.debug('PlaybackEnv')
        self.observation_space = observation_space
        self.action_space = action_space
        self._source = source
        if isinstance(source, Reader):
            if self.observation_space is None:
                self.observation_space = source.observation_space
            if self.action_space is None:
                self.action_space = source.action_space
        self._episodes = iter(source)
        self.episode = -1
        self._steps = iter(())
        self.played_out = False     #: True when input iterable has been exhausted (no more data)
        self._next_episode()
        self.step_num = 0
        self.done = True

    def _next_episode(self):
        while next(self._steps, None) is not None:       # Consume step iterator; important for correctness of iterator.
            pass
        steps = next(self._episodes, None)
        if steps is None:
            self.played_out = True
        else:
            self._steps = iter(steps)

    def _reset(self) -> TObs:
        """:Return: first observation.  Called before the start of every episode."""
        if self.played_out:
            raise ValueError('This PlaybackEnv has exhausted its data.')
        if not self.done:       # reset was called before last episode was done
            self._next_episode()

        data = next(self._steps, None)
        self._log.debug('EP %d STEP 0 RESET: %s', self.episode, data)
        if data is None:
            raise ValueError('Empty episode (no data)')
        self.done = data[DONE]
        self.episode += 1
        self.step_num = 0
        return data[OBS]

    def _step(self, action: TAct) -> TStep[TObs]:
        """:Return: (observation, reward, done, info) for each step."""
        self._log.debug('EP %d STEP %d ACTION: %s', self.episode, self.step_num, action)
        if self.played_out:
            raise ValueError('This PlaybackEnv has exhausted its data.')
        if self.done:
            raise ValueError('Must call reset() before step()')
        data = next(self._steps, None)
        if data is None:
            self.done = True
            # TODO: Consider handling last step not marked done: peek at next step, warn if not marked done.
            raise ValueError('Episode {} exhausted prematurely (last step did not have done = True)'.format(self.episode))

        self.done = data[DONE]
        self.step_num += 1
        if self.done:
            self._next_episode()        # Need to detect / set played_out before reset() is called

        return data[OBS], data[REWARD], data[DONE], data[INFO]

    def _render(self, mode='human', close=False) -> None:
        if mode == 'human':
            if not close:
                print('EP {} STEP {}'.format(self.episode, self.step_num - 1))      # TODO: Show observation

    def _close(self):
        if isinstance(self._source, Reader):
            self._source.close()


class RandomEnv(Generic[TObs, TAct], gym.Env):
    """An environment that generates random observations and rewards for testing.

    Rewards are uniform in the range [0, 1].
    """
    def __init__(self, observation_space: gym.Space, action_space: Optional[gym.Space] = None, episode_steps: int = 10) -> None:        # pylint: disable=bad-whitespace
        """:param action_space: Not used by this environment, but can be set for agents.
        :param episode_steps: Run each episode this number of steps."""
        # TODO: Callables for episode_steps and reward
        super().__init__()
        self.observation_space = observation_space
        self.action_space = action_space
        self.episode_steps = episode_steps
        self.step_num = 0

    def _reset(self) -> TObs:
        self.step_num = 0
        return self.observation_space.sample()

    def _step(self, action: TAct) -> TStep[TObs]:
        """:Return: a random observation, reward in [0, 1], True if done, and an empty info dict."""
        if self.step_num == self.episode_steps:
            raise ValueError('Environment is done; must call reset() before calling step()')
        self.step_num += 1
        return self.observation_space.sample(), np.random.rand(), self.step_num == self.episode_steps, None     # pylint: disable=no-member

    def _seed(self, seed: Optional[int] = None) -> None:
        gym.spaces.prng.seed(seed)

    @property
    def spec(self) -> gym.envs.registration.EnvSpec:
        return gym.envs.registration.EnvSpec('RandomEnv-v0', max_episode_steps=self.episode_steps, nondeterministic=True)


class RandomAgent(Generic[TAct, TObs]):
    """An agent that samples randomly from its action space, ignoring observations."""
    # pylint: disable=too-few-public-methods
    def __init__(self, action_space: gym.Space, seed: Optional[int] = None) -> None:
        self.action_space = action_space
        gym.spaces.prng.seed(seed)

    def act(self, observation: Optional[TObs] = None) -> TAct:      # pylint: disable=unused-argument
        """:Return: a random action sampled from the action space, ignoring `observation`."""
        return self.action_space.sample()


class PlaybackAgent(Generic[TAct, TObs]):
    """An agent that plays back recorded actions, ignoring observations.

    Call :meth:`next_episode` at the start of each episode, then :meth:`act` until :obj:`done`.
    :meth:`next_episode` returns ``False`` when there are no more episodes.
    """
    def __init__(self, source: Union[Reader, Iterable[Iterable[TData]]]) -> None:
        self._source = source
        self._episodes = iter(source)
        self._steps = iter(())
        self._next_step = None

    def next_episode(self) -> bool:
        """Advance to the next episode, return ``False`` if there are no more episodes."""
        while next(self._steps, None) is not None:
            pass        # Exhaust step iterator; important to ensure the iterators don't bork.
        self._steps = iter(next(self._episodes, ()))
        self._next_step = next(self._steps, None)       # First action in an episode is NaN garbage
        self._next_step = next(self._steps, None)
        if self.done and isinstance(self._source, Reader):
            self._source.close()
        return not self.done

    def act(self, observation: Optional[TObs] = None) -> TAct:          # pylint: disable=unused-argument
        """:Return: the next recorded action, ignoring `observation`."""
        if self.done:
            raise ValueError('This episode is exhausted; you must call next_episode() before act().')
        action = self._next_step[ACTION]
        self._next_step = next(self._steps, None)
        return action

    @property
    def done(self) -> bool:
        """True when there is no more data for the current episode."""
        return self._next_step is None

    def __del__(self) -> None:
        if isinstance(self._source, Reader):
            self._source.close()


def serialize_space(space: gym.Space) -> bytes:
    """Serialize a description of a `space` to JSON so recorders can store metadata."""
    # Didn't want to go full importlib here as it complicates things and introduces arbitrary code execution
    # If people want to add custom spaces, this should be a global registry mapping names to ser/de functions.
    if isinstance(space, gym.spaces.Discrete):
        desc = {'name': 'gym.spaces.Discrete', 'args': [space.n]}
    elif isinstance(space, gym.spaces.Box):
        # So it turns out that Box stores `low` and `high` as large arrays, and there is a size limit
        # to the PyTables metadata where we store these serialized spaces (64k).  For typical image spaces,
        # the description is well over 1 MB.  Fortunately, typical image spaces have constant bounds,
        # so we can just detect and use those (together with a shape) instead.
        if np.all(space.low == space.low.flat[0]) and np.all(space.high == space.high.flat[0]):
            args = [space.low.flat[0], space.high.flat[0], space.low.shape]
        else:
            args = [space.low.tolist(), space.high.tolist()]
        desc = {'name': 'gym.spaces.Box', 'args': args}
    else:
        raise ValueError("Unimplemented space '{}'".format(space.__class__.__name__))

    return json.dumps(desc, separators=JSON_COMPACT_SEPARATORS, sort_keys=True).encode('utf8')


def deserialize_space(data: bytes) -> gym.Space:
    """:Return: a :class:`gym.Space` reconstituted from bytes serialized by :func:`serialize_space`."""
    desc = json.loads(data.decode('utf8'))
    name = desc.get('name')
    if name == 'gym.spaces.Discrete':
        return gym.spaces.Discrete(desc['args'][0])
    elif name == 'gym.spaces.Box':
        if len(desc['args']) == 2:      # low, high arrays
            return gym.spaces.Box(np.asarray(desc['args'][0]), np.asarray(desc['args'][1]))
        elif len(desc['args']) == 3:    # low, high scalars + shape
            return gym.spaces.Box(*desc['args'])
        else:
            raise ValueError('Bad Box arguments: {}'.format(desc['args']))
    else:
        raise ValueError("Unimplemented space '{}'".format(name))


def record_from_iter(recorder: Recorder[TObs, TAct], data: Iterable[Iterable[TData[TObs, TAct]]]) -> None:
    """Read from an iterable of episode `data` and record to a `recorder`.
    Can be used to convert formats or test Recorders.
    """
    for episode in data:
        steps = iter(episode)
        recorder.on_reset(*next(steps))
        for step in steps:
            recorder.on_step(*step)
    recorder.on_close()


def generate_random(sample_observation: Callable[[], TObs], sample_action: Callable[[], TObs], sample_reward: Callable[[], float] = np.random.rand, episodes: int = 10, steps_per_episode: Callable[[], int] = lambda: np.random.randint(1, 11)) -> Iterable[Iterable[TData[TObs, TAct]]]:      # pylint: disable=no-member
    """:Return: environment data generated from the given functions.

    Note **you must evaluate every step before the next** or the iterator will be invalid.
    For example: don't store all episodes in a list; store all steps in a list of lists.
    Don't buffer or skip one episode and evaluate the next; iterate over all steps of each episode in order.
    `sample_observation` `sample_action` `sample_reward` are called in that order.
    Returns 1 more item than `steps_per_episode` to account for the initial reset.
    """
    # TODO: info
    for _ in range(episodes):
        steps = steps_per_episode()
        assert steps >= 0
        yield ((time(), sample_observation(), sample_action(), sample_reward(), step == steps, None) for step in range(steps + 1))


def generate_monotonic(episodes: int = 10) -> Iterable[Iterable[TData[np.ndarray, int]]]:
    """:Return: monotonically increasing environment data for testing.

    If ``episode`` is the zero-based episode number, and ``step`` is the zero-based step number within an episode:
    Observation is a pair of ``(episode, step)``; action is ``step``; reward is ``step * 10``, first reward is ``NaN``.
    Episode `i` runs for `i + 1` steps, couting the reset as the first step.
    The observation space is ``Box(0, episodes, shape=(2,))``
    The action space can be treated as either ``Discrete(episodes)`` or ``Box(0, episodes, shape=())``.
    """
    # Avoid making closures in a loop
    def _make_ep(ep_num: int) -> Iterable[TData[np.ndarray, int]]:
        """Generator returning one episode of steps."""
        return ((time(), (ep_num, step), step, step * 10.0 if step else np.nan, step == ep_num + 1, None) for step in range(ep_num + 2))

    for episode in range(episodes):
        yield _make_ep(episode)


def run_episode(env: gym.Env, actions: Optional[Iterable[TAct]] = None, max_steps: Optional[int] = None) -> Optional[Iterable[TData[TObs, TAct]]]:
    """Run an `env` for a single episode and return an iterable of step data.

    Note this may not mark ``done = True`` on the last step if the environment did not return done.
    The first step data returned has "null" action and reward (it should be ignored).
    If `actions` is exhausted, will return None.

    :param actions: Step the environment with these actions and stop when exhausted.
      If None, sample actions randomly from the action space indefinitely.
    :param max_steps: If given, run at most this many steps per episode.
    """
    max_steps = max_steps or sys.maxsize
    actions = actions or itertools.starmap(env.action_space.sample, itertools.repeat(()))
    action = next(actions, None)
    if action is None:
        return None
    obs = env.reset()
    done = False
    step = 0

    yield time(), obs, null_sample(env.action_space), np.nan, done, None

    while step < max_steps and not done and action is not None:
        obs, reward, done, info = env.step(action)
        yield time(), obs, action, reward, done, info
        action = next(actions, None)
        step += 1


def drive_env(env: gym.Env, actions: Optional[Iterable[TAct]] = None, episodes: Optional[int] = None, steps_per_episode: Optional[int] = None) -> Iterable[Iterable[TData[TObs, TAct]]]:
    """Run an `env` and return an iterable of episodes, each an iterable of step data.

    Note this may not mark ``done = True`` on the last step of each episode if the environment did not return done.

    :param actions: Step the environment with these actions and stop when exhausted.
      If None, sample actions randomly from the action space indefinitely.
    :param episodes: If given, run at most this many episodes.
    :param steps_per_episode: If given, run at most this many steps per episode.
    """
    episodes = episodes or sys.maxsize
    for _ in range(episodes):
        steps = run_episode(env, actions, steps_per_episode)
        if steps is None:       # actions exhausted
            break
        yield steps

    env.close()


def getshape(obj: Union[gym.Space, np.ndarray, float]) -> Tuple[int, ...]:
    """:Return: the shape of a :class:`gym.Space` or :class:`np.ndarray`, or ``()`` for a scalar."""
    return getattr(obj, 'shape', ())


def null_sample(space: gym.Space) -> TObs:
    """:Return: NaN or zero or whatever is appropriate as a null (invalid) sample for a given `space`."""
    if isinstance(space, gym.spaces.Discrete):
        return 0
    elif isinstance(space, gym.spaces.Box):
        return np.tile(np.nan, getshape(space))
    else:
        raise ValueError('Unknown space {}'.format(space))


def get_actions(episodes: Iterable[Iterable[TData[TObs, TAct]]]) -> Iterable[Iterable[TAct]]:
    """:Return: an iterable of episode data containing just the valid actions (starting from the 2nd step) from `episodes`."""
    return ((step[ACTION] for step in itertools.islice(episode, 1, None)) for episode in episodes)


def set_done(data: TData[TObs, TAct]) -> TData[TObs, TAct]:
    """:Return: a new data tuple with the `done` field set to `True`."""
    return data[:DONE] + (True,) + data[DONE + 1:]      # starting to sound like a job for a namedtuple...
