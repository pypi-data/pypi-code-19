#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: ploogz.ploogins
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Ploogins and Ploogin Loaders
"""

import os
import importlib.util
import re
import inspect
from abc import ABCMeta, abstractmethod
from typing import Callable, Iterator, List
from automat import MethodicalMachine
from enum import Enum
import inspect

_DEFAULT_SEARCH_PATH = [
    os.path.normpath(os.path.join(os.getcwd(), 'builtin/ploogins'))
]  # The default paths we'll search for ploogins.


class PlooginEvents(Enum):
    """
    These are the well known events that occur in the life cycle of a ploogin.
    """
    SETUP = 'setup',
    ACTIVATE = 'activate',
    TEARDOWN = 'teardown'


class PlooginEventHandler(object):
    """
    Instances of this are callable and wrap handler functions for well-known event ploogin event types.
    """
    def __init__(self,
                 event: PlooginEvents,
                 f: Callable):
        """

        :param event: What type of event does this handler handle?
        :type event:  :py:class:`PlooginEvents`
        :param f: the handler function
        :type f:  Callable
        """
        self._event = event
        self._f = f

    @property
    def event(self) -> PlooginEvents:
        """
        What type of event does this handler handle?
        """
        return self._event

    def __call__(self, *args, **kwargs):
        self._f(*args, **kwargs)


def upon_setup(f: Callable):
    """
    Use this decorator to mark your ploogin function as a handler to call upon setup.
    """
    return PlooginEventHandler(event=PlooginEvents.SETUP, f=f)


def upon_activate(f: Callable):
    """
    Use this decorator to mark your ploogin function as a handler to call upon activation.
    """
    return PlooginEventHandler(event=PlooginEvents.ACTIVATE, f=f)


def upon_teardown(f: Callable):
    """
    Use this decorator to mark you ploogin function as a handler to call upon teardown.
    """
    return PlooginEventHandler(event=PlooginEvents.TEARDOWN, f=f)


class Ploogin(object):
    """
    Extend this class to create your own ploogins!
    """
    __metaclass__ = ABCMeta
    _machine = MethodicalMachine()  # This is the class state machine.

    def __init__(self, name: str):
        """

        :param name: a helpful, descriptive, human-readable name for the plugin
        :type name:  ``str``
        """
        super().__init__()
        self._name = name
        # Get all the event handlers defined for this instance.
        _event_handlers: List[PlooginEventHandler] = [
            tup[1] for tup in inspect.getmembers(self) if isinstance(tup[1], PlooginEventHandler)
        ]
        self._setup_handlers: List[PlooginEventHandler] = [
            eh for eh in _event_handlers if eh.event == PlooginEvents.SETUP
        ]
        self._activation_handlers: List[PlooginEventHandler] = [
            eh for eh in _event_handlers if eh.event == PlooginEvents.ACTIVATE
        ]
        self._teardown_handlers: List[PlooginEventHandler] = [
            eh for eh in _event_handlers if eh.event == PlooginEvents.TEARDOWN
        ]

    @property
    def name(self) -> str:
        """
        Get the helpful, descriptive, human-readable name for the ploogin.

        :rtype: ``str``
        """
        return self._name

    @_machine.state(initial=True)
    def initialized(self):
        """The ploogin has been initialized."""

    @_machine.state()
    def ready(self):
        """The plugin is set up and ready."""

    @_machine.state()
    def active(self):
        """The plugin is active."""

    @_machine.state()
    def torndown(self):
        """The plugin has been torn down."""

    @_machine.input()
    def setup(self, options: dict=None):
        """
        Get the plugin ready to run.

        :param options: the setup options the ploogin should use to prepare itself
        :type options:  ``dict``
        """

    @_machine.output()
    def _setup(self, options: dict=None):
        """
        This is the output method mapped to the :py:func:`Ploogin.setup` input method.

        :param options: the setup options the ploogin should use to prepare itself
        :type options:  ``dict``
        """
        for setup_handler in self._setup_handlers:
            setup_handler(self, options)

    @_machine.input()
    def activate(self):
        """Activate the ploogin."""

    @_machine.output()
    def _activate(self):
        """
        This is the output method mapped to the :py:func:`Ploogin.setup` input method.
        """
        for activation_handler in self._activation_handlers:
            activation_handler(self)

    @_machine.input()
    def teardown(self):
        """Tear down the ploogin."""

    @_machine.output()
    def _teardown(self):
        """
        This is the output method mapped to the :py:func:`Ploogin.teardown` input method.
        """
        for teardown_handler in self._teardown_handlers:
            teardown_handler(self)

    # We start in the 'initialized' state until somebody calls load(), at which point we call the _setup() function and
    # move to the 'ready' state.
    initialized.upon(setup, enter=ready, outputs=[_setup])
    # If we're asked to tear down from the initialized state, that's ok (but nothing happens).
    initialized.upon(teardown, enter=torndown, outputs=[])
    # If we're in the 'ready' state and somebody calls 'activate', call _activate() and move to the 'active' state.
    ready.upon(activate, enter=active, outputs=[_activate])
    # If we're in the 'ready' state and somebody calls 'teardown', call _teardown() and move to the 'torndown' state.
    ready.upon(teardown, enter=torndown, outputs=[_teardown])
    # If we're in the 'active' state and somebody calls 'teardown', call _teardown() and move to the 'torndown' state.
    active.upon(teardown, enter=torndown, outputs=[_teardown])


class PlooginLoader(object):
    """
    Extend this class to create a ploogin loader that can look through search paths to find and instantiate ploogins.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self, search_path: List[str]) -> List[Ploogin]:
        """
        Override this method to implement the loader's primary loading logic.

        :param search_path: the paths the plugin host will search when the ``load()`` method is called
        :type search_path:  List[str]
        """
        pass


class FsPlooginLoader(PlooginLoader):
    """
    This is a ploogin loader that looks for ploogins in the local file system.
    """
    _path_sep_re = re.compile(r":?[\\/\s]", re.IGNORECASE)  # A regular expression that matches file path separators.

    def load(self, search_path: List[str]) -> List[Ploogin]:
        """
        Load the ploogins found in the search paths on the file system.

        :param search_path: the paths the loader will search when the ``load()`` method is called
        :type search_path:  List[str]
        """
        # Clear the current list of ploogins.
        ploogins = []
        # We're going to build up a list of files that may contain modules.
        candidate_module_files = []
        # We need to activate through every search path in the list of search paths.
        for path in search_path:
            # We're going to walk the directory hierarchy.
            for (dirpath, _, filenames) in os.walk(path):
                # Let's look at each filename...
                for filename in filenames:
                    # ...we're only interested in the python modules.
                    if filename.endswith('.py'):
                        # We have a candidate!  Add this module file to the list.  (We'll look for actual ploogins
                        # later.)
                        candidate_module_files.append(os.sep.join([dirpath, filename]))
        # Now let's activate look at those files!
        for candidate_module_file in candidate_module_files:
            # We need to give the module a name.  Let's base it on the file path.
            module_name = self._path_to_module_name(os.path.splitext(candidate_module_file)[0])
            # Now let's import the module.
            spec = importlib.util.spec_from_file_location(module_name, candidate_module_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # For our next trick, we'll need all the module members.
            members = [member for _, member in inspect.getmembers(mod)]
            # But we only want those members that inherit from Ploogin.
            plugin_classes = filter(lambda member: inspect.isclass(member) and Ploogin in member.__bases__, members)
            # Instantiate each plugin class and put the instance in the list.
            for cls in plugin_classes:
                ploogins.append(cls())
        # Return what we got.
        return ploogins

    def _path_to_module_name(self, path: str) -> str:
        """
        Convert a file system path to a module path that can be used when dynamically loading modules.

        :param path: a file system path
        :type path:  ``str``
        :return: the path, converted to conform to a python module name
        :rtype:  ``str``
        """
        return self._path_sep_re.sub('.', path)


class PlooginHost(object):
    """
    Use a host object to load and retrieve your ploogins.
    """
    _machine = MethodicalMachine()  # This is the class state machine.

    def __init__(self,
                 search_path: List[str] or str=None,
                 loader: PlooginLoader=None):
        """

        :param search_path: the paths the plugin host will search when the ``load()`` method is called
        :type search_path:  List[str] or ``str``
        :seealso: :py:func:`PlooginHost.load`

        .. note::
            If no search path is provided, the default path is ``builtin/ploogins`` under the current working directory.
        """
        # Lets figure out what we got for the search path as a parameter value, and turn it into something we can use
        # as we activate along.  (The code below seemed like the more readable wat
        _search_path = None
        if isinstance(search_path, list):
            _search_path = search_path
        elif isinstance(search_path, str):
            _search_path = [search_path]
        elif _search_path is None:
            _search_path = _DEFAULT_SEARCH_PATH
        else:
            raise TypeError('The search_path parameters must be a string or list of strings.')
        self._loader = loader if loader is not None else FsPlooginLoader()
        # What we want in a search path is a list of paths normalized for the operating system.  So, we'll start
        # either with the prescribed list of search paths, and apply the path.normpath() function to each one.
        self._search_path = list(map(lambda p: os.path.normpath(p),  _search_path))
        # Create a variable for the ploogins, but don't populate it with a value yet.  (We'll do that when somebody
        # calls the load() function.)
        self._plugins = None

    @_machine.state(initial=True)
    def initialized(self):
        """The host has been instantiated, but the ploogins have not been loaded yet."""

    @_machine.state()
    def loaded(self):
        """The ploogins have been loaded."""

    @_machine.state()
    def torndown(self):
        """The plugin host has been torn down."""

    @_machine.input()
    def load(self):
        """
        Load the ploogins.
        """

    @_machine.output()
    def _load(self):
        """
        This is the output method associated with the :py:func:`PlooginHost.load` method.

        :seealso: :py:func:`PlooginHost.load`
        """
        # Let the loader do the work.
        self._plugins = self._loader.load(self._search_path)

    @_machine.input()
    def teardown(self):
        """
        Call this method when you're finished with this plugin host, and all the ploogins it has provided.
        """

    @_machine.output()
    def _teardown(self):
        """
        This is the output method associated with the :py:func:`PlooginHost.teardown` method.

        :seealso: :py:func:`PlooginHost.teardown`
        :seealso: :py:func:`Ploogin.teardown`
        """
        # Tear down all the ploogins.
        map(lambda plugin: plugin.teardown(), self._plugins)
        # Clear out the list.
        self._plugins = []

    @property
    def ploogins(self) -> Iterator[Ploogin]:
        """
        Get the ploogins loaded by this host.

        :rtype: :py:class:`Iterator[Ploogin]`
        """
        return iter(self._plugins) if self._plugins is not None else iter([])

    # When the host has just been initialized, we can transition to the 'loaded' state when 'load()' is called.
    initialized.upon(load, enter=loaded, outputs=[_load])
    # We can also transition right to the 'torndown' state from the initial state, but nothing happens.
    initialized.upon(teardown, enter=torndown, outputs=[])
    # If we're all loaded up, we can also tear down.
    loaded.upon(teardown, enter=torndown, outputs=[_teardown])

