#!/usr/bin/env python3

import os
import re
import requests
import argparse
from mako.template import Template
from collections import namedtuple
from pkg_resources import Distribution
try:
    from urllib.parse import urljoin, quote, unquote
except ImportError:
    from urllib import urljoin, quote, unquote

# language=HTML
index_template = Template("""
<html>
<head><title>${project} pip index</title></head>
<body>
<h1>${project}</h1>
    % for package in packages:
        <a href="./${package}.html">${package}</a><br/>
    % endfor
</body>
</html>
""")

# language=HTML
package_template = Template("""
<html>
<head><title>${project} pip index - ${package}</title></head>
<body>
<h1>${package}</h1>
    <ul>
    % for name, url in package_files:
        <li><a href="${url}">${name}</a><br/></li>
    % endfor
    </ul>
</body>
</html>
""")


def main():
    parser = argparse.ArgumentParser(description='Generate python repo index files for all tags in project')
    parser.add_argument('--server', default=None, help='url of gitlab server or $CI_PROJECT_URL')
    parser.add_argument('--project_id', default=None, help='Unique id of project, available in '
                                                           'Project Settings/General or $CI_PROJECT_ID')
    parser.add_argument('--private_token', help='login token if using a private repo')
    parser.add_argument('destination', help='folder to generate html files into')

    args = parser.parse_args()

    headers = None
    if args.private_token:
        headers = {'PRIVATE-TOKEN': args.private_token}

    server = args.server or os.environ['CI_PROJECT_URL']
    if not server:
        print("Must provide --server if not running from CI")
        exit(1)

    project_id = args.project_id or os.environ['CI_PROJECT_ID']
    if not project_id:
        print("Must provide --project_id if not running from CI")
        exit(1)
    project_id = quote(project_id, safe='')

    api_url = urljoin(server, "/api/v4/projects/%s/" % project_id)

    details = requests.get(api_url, headers=headers).json()
    project_url = details['web_url']

    print("Processing tags for %s" % project_url)

    if not server.endswith('/'):
        server += '/'

    if not os.path.exists(args.destination):
        os.makedirs(args.destination)

    rsp = requests.get(urljoin(api_url, 'repository/tags'), headers=headers)
    tags = rsp.json()
    released_file = namedtuple('released_file', ('name', 'url'))
    released_files = {}
    for tag in tags:
        try:
            release = tag['release']
            description = re.findall(r'\[(.*?)\]\((.*)\)', release['description'])
            for name, relurl in description:
                pkg = name.split('-')[0]
                if pkg not in released_files:
                    released_files[pkg] = []
                released_files[pkg].append(released_file(name=name, url=''.join((project_url, relurl))))
        except (KeyError, TypeError):
            pass

    with open(os.path.join(args.destination, 'index.html'), 'w') as indexfile:
        index_page = index_template.render(project=project_url, packages=released_files.keys())
        indexfile.write(index_page)
    for package, package_files in released_files.items():
        with open(os.path.join(args.destination, '{p}.html'.format(p=package)), 'w') as packagefile:
            package_page = package_template.render(project=project_url, package=package, package_files=package_files)
            packagefile.write(package_page)


if __name__ == '__main__':
    main()
