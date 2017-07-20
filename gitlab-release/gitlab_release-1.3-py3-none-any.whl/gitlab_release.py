#!/usr/bin/env python3

import os
import io
import json
import codecs
import zipfile
import argparse
import itertools
import mimetypes
import urllib.error
from glob import glob
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlencode, quote


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        # self.boundary = mimetools.choose_boundary()
        self.boundary = '----------lImIt_of_THE_fIle_eW_$'
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def get_binary(self):
        """Return a binary buffer containing the form data, including attached files."""
        def to_bytes(s):
            return s.encode('ascii') if isinstance(s, str) else s

        part_boundary = '--' + self.boundary

        binary = io.BytesIO()
        needsCLRF = False
        # Add the form fields
        for name, value in self.form_fields:
            if needsCLRF:
                binary.write('\r\n')
            needsCLRF = True

            block = [part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value
            ]
            binary.write('\r\n'.join(block))

        # Add the files to upload
        for field_name, filename, content_type, body in self.files:
            if needsCLRF:
                binary.write('\r\n')
            needsCLRF = True

            block = [part_boundary,
              str('Content-Disposition: file; name="%s"; filename="%s"' % \
              (field_name, filename)),
              'Content-Type: %s' % content_type,
              ''
              ]
            binary.write(b'\r\n'.join([to_bytes(s) for s in block]))
            binary.write(b'\r\n')
            binary.write(to_bytes(body))

        # add closing boundary marker,
        binary.write(to_bytes('\r\n--' + self.boundary + '--\r\n'))
        return binary


def main():
    parser = argparse.ArgumentParser(description='Upload files to gitlab tag (release)')
    parser.add_argument('--server', default=None, help='url of gitlab server or $CI_PROJECT_URL')
    parser.add_argument('--project_id', default=None, help='Unique id of project, available in '
                                                           'Project Settings/General or $CI_PROJECT_ID')
    parser.add_argument('--release_tag', default=None, help='Tag to upload files against or $CI_BUILD_TAG')
    parser.add_argument('--timeout', type=int, default=120, help='Timeout for http requests')
    parser.add_argument('--zip', help='Add all globbed files to provided zip name and upload that')
    parser.add_argument('private_token', help='login token with permissions to commit to repo')
    parser.add_argument('files', nargs="+", help='glob/s of files to upload')

    args = parser.parse_args()

    server = args.server or os.environ['CI_PROJECT_URL']
    if not server:
        print("Must provide --server if not running from CI")
        exit(1)

    project_id = args.project_id or os.environ['CI_PROJECT_ID']
    if not project_id:
        print("Must provide --project_id if not running from CI")
        exit(1)

    release_tag = args.release_tag or os.environ['CI_BUILD_TAG']
    if not release_tag:
        print("Must provide --release_tag if not running from CI")
        exit(1)
        
    print("Uploading to %s (id: %s) @ %s" % (server, project_id, release_tag))

    if not server.endswith('/'):
        server += '/'

    api_url = urljoin(server, "/api/v4/projects/%s/" % project_id)

    all_files = itertools.chain(*[glob(f) for f in args.files])
    
    if args.zip:
        with zipfile.ZipFile(args.zip, "w", zipfile.ZIP_DEFLATED) as zf:
            def zipdir(path, ziph):
                # ziph is zipfile handle
                for root, dirs, files in os.walk(path):
                    for file in files:
                        ziph.write(os.path.join(root, file))

            for fname in all_files:
                print (fname)
                if fname == args.zip:
                    continue
                if os.path.isdir(fname):
                    zipdir(fname, zf)
                else:
                    zf.write(fname)

        all_files = [os.path.abspath(args.zip)]
        
    print("Uploading %s" % all_files)

    error = []
    for fname in all_files:
        with codecs.open(fname, 'rb') as filehandle:

            # Firstly, upload the file to gitlab. This will respond with internal url it's uploaded to
            form = MultiPartForm()
            form.add_file('file', os.path.basename(fname), fileHandle=filehandle, mimetype='application/octet-stream')

            request = Request(urljoin(api_url, 'uploads'))
            request.add_header('PRIVATE-TOKEN', args.private_token)
            # body = bytes(form)
            body = form.get_binary().getvalue()
            request.add_header('Content-type', form.get_content_type())
            request.add_header('Content-length', len(body))
            request.data = body

            try:
                UPLOAD = urlopen(request, timeout=args.timeout).read()
            except:
                print("Failed in initial upload communication to %s" % request.full_url)
                error.append(ex)
                continue
            markdown = json.loads(UPLOAD.decode())['markdown']

            # Now we've got the uploaded file info, attach that to the tag
            data = {'description': markdown}
            request = Request(urljoin(api_url, 'repository/tags/%s/release' % release_tag))
            request.data = urlencode(data).encode()
            request.add_header('PRIVATE-TOKEN', args.private_token)
            try:
                ret = urlopen(request, timeout=args.timeout).read()
            except urllib.error.HTTPError as ex:
                if '409' in str(ex):
                    print("Failed posting upload due to file conflict")
                    print(data)
                else:
                    print("Failed posting upload details to %s" % request.full_url)
                    print(ex)
                error.append(ex)
                continue
                
            except Exception as ex:
                print("Failed posting upload details to %s" % request.full_url)
                print(data)
                print(ex)
                error.append(ex)
                continue
    
            tagname = json.loads(ret.decode())['tag_name']
            print("Uploaded %s to tag %s: %s" % (fname, tagname, urljoin(server, "tags/%s" % quote(tagname))))
    
    if error:
        raise Exception("Finished with errors")

if __name__ == '__main__':
    main()