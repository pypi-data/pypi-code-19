# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

import fnmatch
import hashlib
import itertools
import os.path
import re
from zipfile import ZipFile, ZIP_DEFLATED
from base64 import b64encode, b64decode

from six import PY3, string_types, text_type, python_2_unicode_compatible
from six.moves import cStringIO as StringIO

from asn1crypto import cms, core as asn1core

from . import constants


# Patch asn1crypto teletex codec to actually be latin 1 (iso-8859-1)
# See https://github.com/wbond/asn1crypto/issues/60 and
# https://github.com/mozilla/signing-clients/issues/23 for more details
asn1core.TeletexString._encoding = 'latin1'

headers_re = re.compile(
    r"""^((?:Manifest|Signature)-Version
          |Name
          |Digest-Algorithms
          |(?:MD5|SHA1)-Digest(?:-Manifest)?)
          \s*:\s*(.*)""", re.X | re.I)
continuation_re = re.compile(r"""^ (.*)""", re.I)
directory_re = re.compile(r"[\\/]$")


# partially copied from Django
def force_bytes(s, encoding='utf-8', errors='strict'):
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if not isinstance(s, string_types):
        try:
            if PY3:
                return text_type(s).encode(encoding)
            else:
                return bytes(s)
        except UnicodeEncodeError:
            return text_type(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)


class ParsingError(Exception):
    pass


def ignore_certain_metainf_files(filename):
    """
    We do not support multiple signatures in XPI signing because the client
    side code makes some pretty reasonable assumptions about a single signature
    on any given JAR.  This function returns True if the file name given is one
    that we dispose of to prevent multiple signatures.
    """
    ignore = ("META-INF/manifest.mf",
              "META-INF/*.sf",
              "META-INF/*.rsa",
              "META-INF/*.dsa",
              "META-INF/ids.json")

    for glob in ignore:
        # Explicitly match against all upper case to prevent the kind of
        # runtime errors that lead to https://bugzil.la/1169574
        if fnmatch.fnmatchcase(filename.upper(), glob.upper()):
            return True
    return False


def file_key(zinfo):
    '''
    Sort keys for xpi files
    @param name: name of the file to generate the sort key from
    '''
    # Copied from xpisign.py's api.py and tweaked
    name = zinfo.filename
    prio = 4
    if name == 'install.rdf':
        prio = 1
    elif name in ["chrome.manifest", "icon.png", "icon64.png"]:
        prio = 2
    elif name in ["MPL", "GPL", "LGPL", "COPYING", "LICENSE", "license.txt"]:
        prio = 5
    parts = [prio] + list(os.path.split(name.lower()))
    return "%d-%s-%s" % tuple(parts)


def _digest(data):
    md5 = hashlib.md5()
    md5.update(force_bytes(data))
    sha1 = hashlib.sha1()
    sha1.update(force_bytes(data))
    return {'md5': md5.digest(), 'sha1': sha1.digest()}


@python_2_unicode_compatible
class Section(object):
    __slots__ = ('name', 'algos', 'digests')

    def __init__(self, name, algos=('md5', 'sha1'), digests={}):
        self.name = name
        self.algos = algos
        self.digests = digests

    def __str__(self):
        # Important thing to note: placement of newlines in these strings is
        # sensitive and should not be changed without reading through
        # http://docs.oracle.com/javase/7/docs/technotes/guides/jar/jar.html#JAR%20Manifest
        # thoroughly.
        algos = b''
        order = list(self.digests.keys())
        order.sort()
        for algo in order:
            algos += b' %s' % force_bytes(algo.upper())
        entry = b''
        # The spec for zip files only supports extended ASCII and UTF-8
        # See http://www.pkware.com/documents/casestudies/APPNOTE.TXT
        # and search for "language encoding" for details
        #
        # See https://bugzilla.mozilla.org/show_bug.cgi?id=1013347
        name = b'Name: %s' % force_bytes(self.name)

        # See https://bugzilla.mozilla.org/show_bug.cgi?id=841569#c35
        while name:
            entry += name[:72]
            name = name[72:]
            if name:
                entry += b'\n '
        entry += b'\n'
        entry += b'Digest-Algorithms:%s\n' % force_bytes(algos)
        for algo in order:
            entry += b'%s-Digest: %s\n' % (force_bytes(algo.upper()),
                                           b64encode(self.digests[algo]))
        return entry.decode('utf-8')


@python_2_unicode_compatible
class Manifest(list):
    version = '1.0'
    # Older versions of Firefox crash if a JAR manifest style file doesn't
    # end in a blank line("\n\n").  For more details see:
    # https://bugzilla.mozilla.org/show_bug.cgi?id=1158467
    extra_newline = False

    def __init__(self, *args, **kwargs):
        super(Manifest, self).__init__(*args)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def parse(klass, buf):
        #version = None
        if hasattr(buf, 'readlines'):
            fest = buf
        else:
            fest = StringIO(force_bytes(buf).decode('utf-8'))
        kwargs = {}
        items = []
        item = {}
        header = ''  # persistent and used for accreting continuations
        lineno = 0
        # JAR spec requires two newlines at the end of a buffer to be parsed
        # and states that they should be appended if necessary.  Just throw
        # two newlines on every time because it won't hurt anything.
        for line in itertools.chain(fest.readlines(), "\n" * 2):
            lineno += 1
            line = line.rstrip()
            if len(line) > 72:
                raise ParsingError("Manifest parsing error: line too long "
                                   "(%d)" % lineno)
            # End of section
            if not line:
                if item:
                    items.append(Section(item.pop('name'), **item))
                    item = {}
                header = ''
                continue
            # continuation?
            continued = continuation_re.match(line)
            if continued:
                if not header:
                    raise ParsingError("Manifest parsing error: continued line"
                                       " without previous header! Line number"
                                       " %d" % lineno)
                item[header] += continued.group(1)
                continue
            match = headers_re.match(line)
            if not match:
                raise ParsingError("Unrecognized line format: \"%s\"" % line)
            header = match.group(1).lower()
            value = match.group(2)
            if '-version' == header[-8:]:
                # Not doing anything with these at the moment
                #payload = header[:-8]
                #version = value.strip()
                pass
            elif '-digest-manifest' == header[-16:]:
                if 'digest_manifests' not in kwargs:
                    kwargs['digest_manifests'] = {}
                kwargs['digest_manifests'][header[:-16]] = b64decode(value)
            elif 'name' == header:
                if directory_re.search(value):
                    continue
                item['name'] = value
                continue
            elif 'digest-algorithms' == header:
                item['algos'] = tuple(re.split('\s*', value.lower()))
                continue
            elif '-digest' == header[-7:]:
                if not 'digests' in item:
                    item['digests'] = {}
                item['digests'][header[:-7]] = b64decode(value)
                continue
        if len(kwargs):
            return klass(items, **kwargs)
        return klass(items)

    @property
    def header(self):
        return b"%s-Version: %s" % (
            force_bytes(type(self).__name__.title()),
            force_bytes(self.version))

    @property
    def body(self):
        return b"\n".join([force_bytes(i) for i in self])

    def __str__(self):
        segments = [self.header, b"", self.body]
        if self.extra_newline:
            segments.append(b"")
        return (b"\n".join(
            force_bytes(item) for item in segments)
        ).decode('utf-8')


@python_2_unicode_compatible
class Signature(Manifest):
    omit_individual_sections = True
    digest_manifests = {}
    filename = 'zigbert'

    @property
    def digest_manifest(self):
        return [b"%s-Digest-Manifest: %s" %
                (force_bytes(item[0].upper()), b64encode(item[1]))
                for item in sorted(self.digest_manifests.items())]

    @property
    def header(self):
        segments = [force_bytes(super(Signature, self).header)]
        segments.extend(self.digest_manifest)
        if self.extra_newline:
            segments.append(b"")
        return b"\n".join(force_bytes(item) for item in segments)

    # So we can omit the individual signature sections
    def __str__(self):
        if self.omit_individual_sections:
            return (self.header + b"\n").decode('utf-8')

        if PY3:
            return Manifest.__str__(self)
        else:
            return Manifest.__unicode__(self)


class JarExtractor(object):
    """
    Walks an archive, creating manifest.mf and signature.sf contents as it goes

    Can also generate a new signed archive, if given a PKCS#7 signature
    """

    def __init__(self, path, outpath=None, ids=None,
                 omit_signature_sections=False, extra_newlines=False):
        self.inpath = path
        self.outpath = outpath
        self._digests = []
        self.omit_sections = omit_signature_sections
        self.extra_newlines = extra_newlines
        self._manifest = None
        self._sig = None
        self.ids = ids

        def mksection(data, fname):
            digests = _digest(data)
            item = Section(fname, algos=tuple(digests.keys()),
                           digests=digests)
            self._digests.append(item)
        with ZipFile(self.inpath, 'r') as zin:
            for f in sorted(zin.filelist, key=file_key):
                # Skip directories and specific files found in META-INF/ that
                # are not permitted in the manifest
                if (directory_re.search(f.filename)
                        or ignore_certain_metainf_files(f.filename)):
                    continue
                mksection(zin.read(f.filename), f.filename)
            if ids:
                mksection(ids, 'META-INF/ids.json')

    def _sign(self, item):
        digests = _digest(str(item))
        return Section(item.name, algos=tuple(digests.keys()),
                       digests=digests)

    @property
    def manifest(self):
        if not self._manifest:
            self._manifest = Manifest(self._digests,
                                      extra_newline=self.extra_newlines)
        return self._manifest

    @property
    def signatures(self):
        # The META-INF/*.sf files should contain hashes of the individual
        # sections of the the META-INF/manifest.mf file.  So we generate those
        # signatures here
        if not self._sig:
            self._sig = Signature([self._sign(f) for f in self._digests],
                                  digest_manifests=_digest(force_bytes(self.manifest)),
                                  omit_individual_sections=self.omit_sections,
                                  extra_newline=self.extra_newlines)
        return self._sig

    @property
    def signature(self):
        # Returns only the x-Digest-Manifest signature and omits the individual
        # section signatures
        return self.signatures.header + b"\n"

    def make_signed(self, signature, outpath=None, sigpath=None):
        outpath = outpath or self.outpath
        if not outpath:
            raise IOError("No output file specified")

        if os.path.exists(outpath):
            raise IOError("File already exists: %s" % outpath)

        sigpath = sigpath or self.signatures.filename
        # Normalize to a simple filename with no extension or prefixed
        # directory
        sigpath = os.path.splitext(os.path.basename(sigpath))[0]
        sigpath = os.path.join('META-INF', sigpath)

        with ZipFile(self.inpath, 'r') as zin:
            with ZipFile(outpath, 'w', ZIP_DEFLATED) as zout:
                # The PKCS7 file("foo.rsa") *MUST* be the first file in the
                # archive to take advantage of Firefox's optimized downloading
                # of XPIs
                zout.writestr("%s.rsa" % sigpath, signature)
                for f in zin.infolist():
                    # Make sure we exclude any of our signature and manifest
                    # files
                    if ignore_certain_metainf_files(f.filename):
                        continue
                    zout.writestr(f, zin.read(f.filename))
                zout.writestr("META-INF/manifest.mf", str(self.manifest))
                zout.writestr("%s.sf" % sigpath, str(self.signatures))
                if self.ids is not None:
                    zout.writestr('META-INF/ids.json', self.ids)


class SignatureInfo(object):

    def __init__(self, pkcs7):
        if isinstance(pkcs7, SignatureInfo):
            # Allow passing around SignatureInfo objects to avoid
            # re-reading the signature every time.
            self.content = pkcs7.content
        else:
            self.content = cms.ContentInfo.load(pkcs7).native['content']

    @property
    def signer_serial_number(self):
        return self.signer_info['sid']['serial_number']

    @property
    def signer_info(self):
        """There should be only one SignerInfo for add-ons,
        nss doesn't support multiples

        See ttps://bugzilla.mozilla.org/show_bug.cgi?id=1357815#c4 for a few
        more details.
        """
        return self.content['signer_infos'][0]

    @property
    def issuer(self):
        return self.signer_info['sid']['issuer']

    @property
    def signer_certificate(self):
        for certificate in self.content['certificates']:
            info = certificate['tbs_certificate']
            if info['issuer'] == self.issuer and info['serial_number'] == self.signer_serial_number:
                return info


def get_signer_serial_number(pkcs7):
    """Return the signer serial number of the signature."""
    return SignatureInfo(pkcs7).signer_serial_number


def get_signer_organizational_unit_name(pkcs7):
    """Return the OU of the signer certificate."""
    return SignatureInfo(pkcs7).signer_certificate['subject']['organizational_unit_name']
