from pathlib import Path

from blobstash.base.client import Client
from blobstash.base.error import BlobStashError


class FileTreeError(BlobStashError):
    """Base error for the filetree modue."""


class Node:
    def __init__(self, name, ref, size, type_, url, metadata):
        self.name = name
        self.ref = ref
        self.size = size
        self.type = type_
        self.url = url
        self.metadata = metadata

    @classmethod
    def from_resp(cls, node):
        return cls(
            name=node['name'],
            ref=node['ref'],
            size=node['size'],
            type_=node['type'],
            url=node['url'],
            metadata=node['metadata'],
        )

    def __repr__(self):
        return 'Node(name={!r}, ref={!r}, type={!r})'.format(
            self.name,
            self.ref,
            self.type,
        )


class FileTreeClient:
    """BlobStash FileTree client."""

    def __init__(self, base_url=None, api_key=None):
        self._client = Client(base_url=base_url, api_key=api_key)

    def fput_node(self, name, fileobj, content_type=None):
        """Upload the fileobj as name, and return the newly created node."""
        return Node.from_resp(self._client.request(
            'POST',
            '/api/filetree/upload',
            files=[
                ('file', (name, fileobj, content_type)),
            ],
        ))

    def put_node(self, path):
        """Uppload the file at the given path, and return the newly created node."""
        name = Path(path)
        with open(path, 'rb') as f:
            return self.fput_node(name, f)

    def fget_node(self, ref):
        """Returns a file-like object for given node ref.

        It's up to the client to call `close` to release the connection.

        """
        if isinstance(ref, Node):
            ref = ref.ref
        return self._client.request('GET', '/api/filetree/file/'+ref, raw=True, stream=True).raw

    def get_node(self, ref, path):
        """Download the content of the given node at path."""
        with open(path, 'rb') as f:
            reader = self.fget_node(ref)
            try:
                while 1:
                    chunk = reader.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            except:
                reader.close()
                raise

    def node(self, ref):
        """Returns the node for the given ref."""
        return Node.from_resp(self._client.request('GET', '/api/filetree/node/'+ref))

    def __repr__(self):
        return 'blobstash.docstore.FileTreeClient(base_url={!r})'.format(self._client.base_url)

    def __str__(self):
        return self.__repr__()
