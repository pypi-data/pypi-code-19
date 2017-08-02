"""
thing.py
We really wanted to name this object.py, but object is taken!
This will be the base class of non-agent thingies that are
in the same environment as agents, e.g., resources, obstacles,
and so on.
"""

# import logging
import indra.entity as ent


class Thing(ent.Entity):
    """
    The base class of all non-agent components in an env.
    For now, we will assume they have a location in space.
    """

    def __init__(self, name, x, y):
        super().__init__(name)
        self.pos = (x, y)
