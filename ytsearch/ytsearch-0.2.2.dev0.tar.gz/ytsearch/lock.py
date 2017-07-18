#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time


class Open:
    """
    A wrapper around open() that implements a lock file.
    """
    def __init__(self, filepath, *args, **kwargs):
        """
        Create the instance, this part waits for the lock.

        :filepath: str: The path of the file to open.
        :*args: list: The rest of the arguments passed.
        :**kwargs: dict: The keyword arguments passed.
        """
        self._filepath = filepath
        locked = self.wait_for_lock() 
        if locked:
            self._file = None
        else:
            self._file = open(filepath, *args, **kwargs)

    def wait_for_lock(self):
        """
        Wait for the lock to be removed. It will only wait for
        10 seconds before it fails.

        :return: bool: True if the this instance has rights
                       over the file. False otherwise.
        """
        lockfile = '{}.lock'.format(self._filepath)
        for i in range(10):
            if not os.path.exists(lockfile):
                return False
            time.sleep(1)
        return True

    def lock(self):
        """Create the lockfile."""
        lockfile = '{}.lock'.format(self._filepath)
        with open(lockfile, 'w') as f:
            f.write('locked')
        return None

    def unlock(self):
        """Remove the lockfile."""
        lockfile = '{}.lock'.format(self._filepath)
        os.remove(lockfile)
        return None

    def __enter__(self):
        self.lock()
        return self._file

    def __exit__(self, *_):
        self.unlock()
        return None
