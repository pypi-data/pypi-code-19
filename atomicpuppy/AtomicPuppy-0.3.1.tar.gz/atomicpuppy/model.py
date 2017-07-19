class Event:

    def __init__(self, id, type, data, stream, sequence):
        self.id = id
        self.type = type
        self.data = data
        self.stream = stream
        self.sequence = sequence

    def __str__(self):
        return "{}/{}-{} ({}): {}".format(
            self.stream,
            self.type,
            self.sequence,
            self.id,
            self.data
        )


class SubscriberInfo:

    def __init__(
            self,
            stream,
            uri,
            last_read=-1):
        self._stream = stream
        self._uri = uri
        self._last_read = last_read

    @property
    def stream(self):
        return self._stream

    @property
    def last_read(self):
        return self._last_read

    @property
    def uri(self):
        return self._uri


class Page:

    def __init__(self, js, logger):
        self._js = js
        self._logger = logger

    def is_empty(self):
        # TODO: I'm not certain what types js["entries"] can have.  Find out
        # and remove any un-needed calls of this method (I'm assuming only type
        # list).
        return not self._js["entries"]

    def is_event_present(self, event_number):
        for e in self._js["entries"]:
            if e["positionEventNumber"] <= event_number:
                return True
        else:
            return False

    def iter_events_since(self, event_number):
        for e in reversed(self._js['entries']):
            if e["positionEventNumber"] > event_number:
                evt = self._make_event(e)
                if evt is not None:
                    yield evt

    def iter_events_matching(self, predicate):
        if not self.is_empty():
            for e in self._js["entries"]:
                evt = self._make_event(e)
                if evt is None:
                    continue
                if predicate(evt):
                    self._logger.info('Found first matching event: %s', evt)
                    yield evt

    def get_link(self, rel):
        for link in self._js["links"]:
            if(link["relation"] == rel):
                return link["uri"]

    def _make_event(self, e):
        try:
            data = json.loads(e["data"], encoding='UTF-8')
        except KeyError:
            # Eventstore allows events with no `data` to be posted. If that
            # happens, then atomicpuppy doesn't know what to do
            self._logger.warning(
                "No `data` key found on event {}".format(e))
            return None
        except ValueError:
            self._logger.error(
                "Failed to parse json data for %s message %s",
                e.get("eventType"), e.get("eventId"))
            return None
        type = e["eventType"]
        id = UUID(e["eventId"])
        stream = e["positionStreamId"]
        sequence = e["positionEventNumber"]
        return Event(id, type, data, stream, sequence)


