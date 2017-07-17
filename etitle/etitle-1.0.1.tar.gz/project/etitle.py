# MIT License
# Copyright (c) 2017 David Betz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import datetime

poundre = "^#([0-9]+)#(.*)"
doubleequalsre = "==([A-Za-z0-9]+)"
titleFileName = '.titles'

DEBUG = False

def output(*args):
    if DEBUG:
        if len(args) == 0:
            print()
        else:
            text, = args
            print(text)

def parse(input, base, *args):
    options = {}

    if len(args) > 0:
        options, = args

    if 'labelMode' not in options:
        options['labelMode'] ='root'

    return process_selector(input, base, options)

def parse_using_title_data(input, base, *args):
    options = {}

    if len(args) > 0:
        options, = args

    if 'labelMode' not in options:
        options['labelMode'] ='root'

    output()
    output('parse_using_title_data|input:{}|base:{}|options:{}'.format(input, base, options))

    parent = re.sub(r"\\", "/", os.path.dirname(input))

    if 'titleData' in options and len(options['titleData']) > 0:
        return process_selector(input, base, options)

    options['titleData'] = create_effective_title_data(parse_title_data(base), parse_title_data(parent))

    return process_selector(input, base, options)

def create_selector(key, *args):
    allowHyphensInSelector = ''
    keepDot = ''

    if len(args) ==2:
        allowHyphensInSelector, keepDot = args
    elif len(args)==1:
        allowHyphensInSelector, = args

    output()
    output('create_selector|key:{}|args:{}|allowHyphensInSelector:{}|keepDot:{}'.format(key,args,allowHyphensInSelector,keepDot))

    if key is None:
        return ''

    if key.find("==") > -1:
        partArray = key.split('/')
        list = []
        for part in partArray:
            if part.find("==") > -1:
                doubleequalsresult = re.search(doubleequalsre, part)
                if doubleequalsresult != None:
                    item = doubleequalsresult.group(1)
                    list.append(item.strip())
            else:
                list.append(part)

        key = "/".join([str(_) for _ in list])

    key = key.replace('%questionmark%', "?").replace('%colon%', ":")
    key = key.replace('%quotes%', "\"").replace('%slash%', "/")
    key = key.replace('%blackslash%', "\\").replace(' ', '').strip().lower()

    key = remove_each_exception(key)

    key = re.sub('[^A-Za-z0-9\/{}{}]+'.format(("-" if allowHyphensInSelector else ''), ("\\." if keepDot else '')), '', key)

    output('~create_selector:{}'.format(key))

    return key

def create_effective_title_data(rootTitleData, relativeTitleData):
    output()
    output('create_effective_title_data|rootTitleData:{}|relativeTitleData:{}'.format(rootTitleData, relativeTitleData))

    effectiveTitleData = rootTitleData

    output('->rootTitleData => {}'.format(rootTitleData))

    if len(relativeTitleData) > 0:
        effectiveTitleData = [v for v in rootTitleData if not any(v['key'] == p['key'] for p in relativeTitleData)]

    result = effectiveTitleData + relativeTitleData

    output('~create_effective_title_data => {}'.format(result))

    return result

def transform_title_data(data):
    output()
    output('transform_title_data|data:{}'.format(data))
    def transform(line):

        index = line.find(',')
        if index == -1:
            return None

        key = line[:index].strip()
        title = line[index + 1:].strip()

        return {
            "key": key,
            "title": title
        }

    result = [transform(_) for _ in data.split('\n')]

    output('~transform_title_data:{}'.format(result))

    return result

def parse_title_data(titleFolder) :
    titleFile = os.path.join(titleFolder, titleFileName)

    output()
    output('parse_title_data|titleFile:{}'.format(titleFile))

    if os.path.exists(titleFile):
        with open(titleFile) as f:
            result = transform_title_data(f.read())
            output('~parse_title_data:{}'.format(result))
            return result

def clean(path) :
    output()
    output('clean|path:{}'.format(path))

    if path[0] == '/':
        path = path[1:]
        #path = path.substring(1)
    if path[len(path) - 1] == '/':
        path = path[:-1]
        #path = path.substring(0, len(path) - 1)

    output('~clean:{}'.format(path))

    return path

def process_selector(input, base, options) :
    output()
    output('process_selector|input:{}|base:{}|options:{}'.format(input, base, options))

    try:
        allowHyphensInSelector = options['allowHyphensInSelector']
    except:
        allowHyphensInSelector = ''

    try:
        labelMode = options['labelMode']
    except:
        labelMode = ''

    parent = os.path.dirname(input).replace('\\', "/")
    input = clean(input[len(base):]).replace('\\', "/")
    name = os.path.basename(input).replace('\\', "/")
    input = clean(input[:-len(name)])
    base = base.replace('\\', "/")
    lastDot = name.rfind(".")
    filename = name[:lastDot]
    [key, title] = get_key_and_title(filename, allowHyphensInSelector)
    semicolonIndex = filename.find(";")
    url = input.replace('\\', '/')
    branch_title = format_branch_name(url.split('/')[0])
    branchesToRoot = create_selector(url)
    selector = create_selector(clean(url) + '/' + key, allowHyphensInSelector)
    branch = create_selector(url.split('/')[0] or '', allowHyphensInSelector)

    try:
        titleData = options['titleData']
    except:
        titleData = ''

    title = clean_title(selector, title, titleData).strip()

    labels = []
    if semicolonIndex > 0 and filename[semicolonIndex - 1] != '/':
        output('->semicolonIndex:{}|filename[semicolonIndex + 1: -len(filename):{}'.format(semicolonIndex, filename[semicolonIndex + 1: -len(filename)]))
        labels = labels + [create_selector(_) for _ in filename[semicolonIndex + 1:].split(';')]

    if labelMode == 'root' and branch:
        labels.append(branch)
    elif labelMode == 'branch' and branchesToRoot:
        labels.append(branchesToRoot)
    elif labelMode == 'each' and branchesToRoot:
        labels = labels + [_ for _ in branchesToRoot.split('/')]

    output('~process_selector:{}'.format((selector, branch, title, branch_title, labels)))

    return (selector, branch, title, branch_title, labels)

def clean_title(key, title, titleData):
    output()
    output('clean_title|key:{}|title:{}|titleData:{}'.format(key, title, titleData))

    if title == None:
        return ''

    if title == "$" or titleData:
        newTitleArray = [_ for _ in titleData if _['key'] == key]
        output('----------------------newTitleArray:{}'.format(newTitleArray))
        if len(newTitleArray) > 0:
            newTitle = newTitleArray[0]
            title = newTitle['title']

    title = title.replace('{', '').replace('}', '').replace('%questionmark%', "?")
    title = title.replace('%colon%', ":").replace('%quotes%', "\"").replace('%slash%', "/")
    title = title.replace('%blackslash%', "\\")

    if title == "$":
        title = ''

    output('~clean_title:{}'.format(title))

    return title

def get_key_and_title(path, allowHyphensInSelector):
    output()
    output('get_key_and_title|path:{}|allowHyphensInSelector:{}'.format(path, allowHyphensInSelector))

    key=''
    title=''
    semicolonIndex = path.find(";")

    if semicolonIndex > 0 and path[semicolonIndex - 1] != '/':
        path = path[:semicolonIndex]
        #path = path.substring(0, semicolonIndex)

    if path.startswith("#"):
        poundresult = re.search(poundre, line)
        if poundresult != None:
            path = poundresult.group(1)
            path = path.strip()

    if path.startswith("=="):
        doubleequalsresult = re.search(doubleequalsre, line)
        if doubleequalsresult != None:
            key = doubleequalsresult.group(1)
            return [key.strip(), '']
    elif path.find("==") > -1:
        doubleequalsresult = re.search(doubleequalsre, line)
        if doubleequalsresult != None:
            key = doubleequalsresult.group(1)
            return [key.strip(), title]

    output('->path:{}'.format(path))

    if path.find(" - ") > -1:
        pathPartArray = path.split('-')

        if pathPartArray[0].strip() == "$":
            title = "$"
            key = pathPartArray[1].strip()
        else :
            title = pathPartArray[1].strip()
            key = pathPartArray[0].strip()
    else:
        key = path
        title = path

    output('->1key:{}'.format(key))
    key = create_selector(key, allowHyphensInSelector)

    output('->2key:{}'.format(key))
    title = title.strip()

    output('~get_key_and_title:{}'.format([key, title]))

    return [key, title]

def remove_each_exception(text):
    output()
    output('remove_each_exception|text:{}'.format(text))

    inside = False
    escaped = False
    newString = ''

    for location in range(len(text)):
        current = text[location]

        if current == '\\':
            escaped = not escaped

        elif current == '{' and not escaped:
            inside = True

        elif current == '}' and inside and not escaped:
            inside = False

        elif inside:
            escaped = False

        else:
            newString += current
            escaped = False

    output('~remove_each_exception:{}'.format(newString))

    return newString

def format_branch_name(name):
    output()
    output('format_branch_name|name:{}'.format(name))

    sb = []
    name = name.replace('{', "").replace('}', "").replace('==', " ")

    output('->name:{}'.format(name))

    n = 0
    length = len(name)
    while True:
        if n == length:
            result = ''.join([str(_) for _ in sb]).strip()
            output('~format_branch_name:{}'.format(result))
            return result

        c = name[n]

        if c == '_' and n + 1 < length:
            sb.append(" " + name[n + 1].lower())
            n = n + 1
        elif c == '=' and n + 1 < length:
            sb.append(" " + name[n + 1].upper())
            n = n + 1
        elif c == ' ' and n + 1 < length:
            if name[n + 1] == '=' or name[n + 1] == '_':
                n = n + 1
                continue
            sb.append(" " + name[n + 1].upper())
            n = n + 1
        elif n == 0:
            sb.append(name[n].upper())
        else:
            sb.append(c)

        n = n + 1