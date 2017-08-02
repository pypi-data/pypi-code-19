import tempfile, shutil, os, json, time
import segment_source.domain_pb2 as service
from io import IOBase

class SourceLogger(object):

    def __init__(self, client=None, source=None, version=None):
        """Creates a new Source Logger object"""
        self.client = client
        self.source = source
        self.version = version

    def collection_started(self, collection=None):
        self.__write(collection=collection,
                     level="info",
                     operation="collection started")

    def collection_finished(self, collection=None):
        self.__write(collection=collection,
                     level="info",
                     operation="collection finished")

    def request_sent(self, collection=None, query=None, metadata=None):
        if metadata:
            md = metadata.copy()
        else:
            md = {}

        if query:
            md["query"] = query

        self.__write(collection=collection,
                     level="info",
                     operation="request sent",
                     metadata=md)

    def response_received(self, collection=None, query=None, metadata=None, latency=None, payload=None):
        if metadata:
            md = metadata.copy()
        else:
            md = {}

        if query:
            md["query"] = query

        if latency:
            md["request_latency"] = int(latency.total_seconds() * 1000)

        self.__write(collection=collection,
                     level="info",
                     operation="response received",
                     metadata=md,
                     payload=payload)

    def error(self, collection=None, operation=None, error=None):
        self.__write(collection=collection,
                     level="error",
                     operation="error encountered",
                     metadata={"operation": operation, "message":error})

    def __write(self, collection=None, level=None, operation=None, id=None, metadata=None, payload=None):

        filename = None

        if payload:
            try:
                if isinstance(payload, IOBase):
                    filename = self.__write_file(payload)
                elif isinstance(payload, int): # file descriptor
                    filename = self.__write_file_handle(payload)
                elif isinstance(payload, str):
                    filename = self.__write_string(payload)
                else:
                    filename = self.__write_object(payload)
            except Exception as e:
                self.error(collection=collection,operation="writing payload",error="Type:{}\n{}".format(str(type(payload)),str(e)))

        if metadata:
            md = json.dumps(metadata)
        else:
            md = None

        request = service.LogRequest(collection=collection,
                                     level=level,
                                     timestamp=int(time.time()),
                                     operation=operation,
                                     attributes=md,
                                     id=id,
                                     filename=filename)
        self.client.LogSourceEntry(request, 30)

    def __write_file_handle(self, fd=None):
        file = os.fdopen(fd, 'wb')
        # if we close file, it will also close fd
        # so must leave open for the caller to close
        return self.__write_file(file)

    def __write_file(self, f=None):
        f.seek(0, 0)
        fd, path = tempfile.mkstemp()
        file = os.fdopen(fd, 'wb')
        shutil.copyfileobj(f, file)
        file.close()
        f.seek(0, 0)
        return path
        
    def __write_object(self, obj=None):
        fd, path = tempfile.mkstemp(text=False)
        file = os.fdopen(fd, 'w')
        json.dump(obj, file)
        file.close()
        return path

    def __write_string(self, pl=None):
        fd, path = tempfile.mkstemp()
        os.write(fd, pl.encode('utf-8'))
        os.close(fd)
        return path
