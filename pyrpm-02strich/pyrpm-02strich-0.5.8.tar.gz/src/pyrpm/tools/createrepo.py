import gzip
import hashlib
from io import BytesIO
import os
import os.path

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

from future.utils import iteritems


def register_namespace(name, ns):
    if ElementTree.VERSION[0:3] == '1.2':
        ElementTree._namespace_map[ns] = name if name else None
    else:
        # For etree > 1.3, use register_namespace function
        ElementTree.register_namespace(name, ns)


class YumRepository(object):

    def __init__(self, repodir):
        self.repodir = repodir
        self.primary_data = {}
        self.filelists_data = {}
        self.other_data = {}

    def read(self):
        # open repomd to find xml files
        with self._retr_file('repodata/repomd.xml') as file:
            repomd_tree = ElementTree.parse(file)

        # read XML files
        for type, dictionary, node_filter, id_func in [
                ('primary', self.primary_data, "{http://linux.duke.edu/metadata/common}package", lambda x: x.find('{http://linux.duke.edu/metadata/common}checksum[@pkgid="YES"]').text),
                ('filelists', self.filelists_data, "{http://linux.duke.edu/metadata/filelists}package", lambda x: x.attrib['pkgid']),
                ('other', self.other_data, "{http://linux.duke.edu/metadata/other}package", lambda x: x.attrib['pkgid'])]:

            # find location
            node = repomd_tree.find("{http://linux.duke.edu/metadata/repo}data[@type='" + type + "']")
            if node is None:
                continue

            # parse file
            self._read_meta(node.find('{http://linux.duke.edu/metadata/repo}location').get('href', None), dictionary, node_filter, id_func)

    def save(self):
        # create XML files
        primary_file, primary_file_gz = self._create_meta(self.primary_data, '{http://linux.duke.edu/metadata/common}metadata', 'http://linux.duke.edu/metadata/common')
        filelists_file, filelists_file_gz = self._create_meta(self.filelists_data, '{http://linux.duke.edu/metadata/filelists}filelists', 'http://linux.duke.edu/metadata/filelists')
        other_file, other_file_gz = self._create_meta(self.other_data, '{http://linux.duke.edu/metadata/other}otherdata', 'http://linux.duke.edu/metadata/other')

        # create repomd
        tree = ElementTree.ElementTree(ElementTree.Element("{http://linux.duke.edu/metadata/repo}repomd"))

        # compute file-stuff
        for type, file, file_gz, filename in [
                ('primary', primary_file, primary_file_gz, 'repodata/primary.xml.gz'),
                ('filelists', filelists_file, filelists_file_gz, 'repodata/filelists.xml.gz'),
                ('other', other_file, other_file_gz, 'repodata/other.xml.gz')]:

            # compute file numbers (size, checksum)
            open_size = file.tell()
            open_checksum = self._hash(file)
            normal_size = file_gz.tell()
            normal_checksum = self._hash(file_gz)

            # create XML
            e = ElementTree.Element("{http://linux.duke.edu/metadata/repo}data", {'type': type})
            self._add_node(e, "{http://linux.duke.edu/metadata/repo}checksum", {'type': 'sha256'}, text=normal_checksum)
            self._add_node(e, "{http://linux.duke.edu/metadata/repo}size", text=str(normal_size))
            self._add_node(e, "{http://linux.duke.edu/metadata/repo}open-checksum", {'type': 'sha256'}, text=open_checksum)
            self._add_node(e, "{http://linux.duke.edu/metadata/repo}open-size", text=str(open_size))
            self._add_node(e, "{http://linux.duke.edu/metadata/repo}location", {'href': filename})
            tree.getroot().append(e)

            # write files
            self._store_file(file_gz, filename)

            # close files
            file.close()
            file_gz.close()

        # map namespaces
        register_namespace('rpm', 'http://linux.duke.edu/metadata/rpm')
        register_namespace('', 'http://linux.duke.edu/metadata/repo')

        # write everything out
        file = BytesIO()
        file.write("<?xml version='1.0' encoding='utf-8'?>\n".encode('utf-8'))
        tree.write(file, encoding='utf-8')
        self._store_file(file, 'repodata/repomd.xml')
        file.close()

    def packages(self):
        for key, value in iteritems(self.primary_data):
            yield (key, value, self.filelists_data[key], self.other_data[key])

    def add_package(self, package, clog_limit=0):
        pkgid = package.checksum

        self.primary_data[pkgid] = package.xml_primary_metadata(self.repodir)
        self.filelists_data[pkgid] = package.xml_filelists_metadata()
        self.other_data[pkgid] = package.xml_other_metadata(clog_limit)

    def remove_package(self, pkgid):
        for part in (self.primary_data, self.filelists_data, self.other_data):
            if pkgid in part:
                del part[pkgid]

    def _read_meta(self, location, dictionary, search_str, id_func):
        if not location:
            return

        # parse primary XML
        with self._retr_file(location) as file:
            file_gz = gzip.GzipFile(fileobj=file)
            tree = ElementTree.parse(file_gz)
            file_gz.close()

        # read package nodes
        for pkg_node in tree.findall(search_str):
            dictionary[id_func(pkg_node)] = pkg_node

    def _create_meta(self, package_list, root_tag, local_namespace):
        # create complete document
        tree = ElementTree.ElementTree(ElementTree.Element(root_tag))
        tree.getroot().set('packages', str(len(package_list)))
        for pkg_node in package_list.items():
            tree.getroot().append(pkg_node[1])

        # map namespaces
        register_namespace('rpm', 'http://linux.duke.edu/metadata/rpm')
        register_namespace('', local_namespace)

        # write it out
        output = BytesIO()
        output_gz = BytesIO()
        primary_file = gzip.GzipFile(fileobj=output_gz, mode='w')
        for file_obj in (output, primary_file):
            file_obj.write("<?xml version='1.0' encoding='utf-8'?>\n".encode('utf-8'))
            tree.write(file_obj, 'utf-8')

        return output, output_gz

    def _retr_file(self, filename):
        return open(os.path.join(self.repodir, filename), 'rb')

    def _store_file(self, file, filename):
        # check for folder
        if not os.path.exists(os.path.dirname(os.path.join(self.repodir, filename))):
            os.mkdir(os.path.dirname(os.path.join(self.repodir, filename)))

        # store file
        file.seek(0)
        with open(os.path.join(self.repodir, filename), 'wb') as fs_file:
            data = file.read()
            while data:
                fs_file.write(data)
                data = file.read()

    def _hash(self, file):
        file.seek(0)
        m = hashlib.sha256()
        data = file.read()
        while data:
            m.update(data)
            data = file.read()
        return m.hexdigest()

    def _add_node(self, parent, tag, attrib={}, text=None):
            a = ElementTree.Element(tag, attrib)
            if text is not None:
                a.text = text
            parent.append(a)
