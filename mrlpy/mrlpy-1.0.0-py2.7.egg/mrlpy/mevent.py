class MEvent( object ):
    """
    Event object to use with MEventDispatch.
    """

    def __init__(self, event_type):
        """
        The constructor accepts an event type as string
        """
        self._type = event_type

    @property
    def type(self):
        """
        Returns the event type
        """
        return self._type

    @property
    def data(self):
        """
        Returns the data associated to the event
        """
        return self._data
