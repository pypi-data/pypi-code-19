# ------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012 -2017 Luzzi Valerio
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        http
# Purpose:
#
# Author:      Luzzi Valerio
# Created:     15/02/2013
# ----------------------------------------------------------------------------

import json
from cgi import FieldStorage

from filesystem import *
from gecosistema_lite.sqlitedb import SqliteDB


class Form:
    """
    Form
    """

    def __init__(self, environ):
        try:
            form = get_post_form(environ)
            self.form = {}
            for key in form:
                value = form.getvalue(key)
                self.form[key] = value
        except:
            _environ = {}
            for key in environ:
                value = environ[key]
                _environ[key] = value
            self.form = _environ

    def keys(self):
        """
        keys
        """
        return self.form

    def getvalue(self, key, default=None):
        """
        getvalue
        """
        if self.form.has_key(key):
            return self.form[key]
        else:
            return default

    def toObject(self):
        """
        toObject
        """
        return self.form


class InputProcessed(object):
    """
    InputProcessed
    """

    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')

    readline = readlines = __iter__ = read


def get_post_form(environ):
    """
    get_post_form
    """
    input = environ['wsgi.input']
    post_form = environ.get('wsgi.post_form')
    if post_form is not None and post_form[0] is input:
        return post_form[2]
    # This must be done to avoid a bug in cgi.FieldStorage
    environ.setdefault('QUERY_STRING', '')
    form = FieldStorage(fp=input, environ=environ, keep_blank_values=1)
    new_input = InputProcessed()
    post_form = (new_input, input, form)
    environ['wsgi.post_form'] = post_form
    environ['wsgi.input'] = new_input
    return form


def doNotRespond(status, response_headers):
    """
    doNotRespond
    """
    pass


def httpResponse(text, status, start_response):
    """
    httpResponse
    """
    text = "%s" % str(text)
    response_headers = [('Content-type', 'text/html'), ('Content-Length', str(len(text)))]
    if start_response:
        start_response(status, response_headers)
    return [text]


def httpResponseOK(text, start_response):
    """
    httpResponseOK
    """
    return httpResponse(text, "200 OK", start_response)


def httpResponseNotFound(start_response):
    """
    httpResponseNotFound
    """
    return httpResponse("404 NOT FOUND", "404 NOT FOUND", start_response)


def httpResponseError(start_response, text="500 Internal Error"):
    """
    httpResponseError
    """
    return httpResponse(text, "500 Internal Error", start_response)


def JSONResponse(obj, start_response):
    """
    JSONResponse
    """
    if isinstance(obj, (str, unicode)):
        res = obj
    elif isinstance(obj, (dict, list)):
        res = unicode(json.dumps(obj))
    else:
        res = obj
    return httpResponse(res, "200 OK", start_response)


def SQLResponse(db, sql, env={}, start_response=None, savequery=False, verbose=False):
    """
    SQLResponse
    """

    # find the query on the sever----------------------------------------------
    filesql, sql_stored = "", ""
    if savequery:
        filesql = sformat("""{workdir}/lib/sql/{md5}.sql""", {"workdir": justpath(__file__, 3), "md5": md5text(sql)})
        sql_stored = filetostr(filesql)
        if not sql_stored:
            return JSONResponse({"status": "fail", "exception": "Acess denied", "sql": sql}, start_response)
        else:
            sql = sql_stored
    # -------------------------------------------------------------------------

    (filexls, sheetname) = SqliteDB.GetTablenameFromQuery(sql)

    db = db if db else SqliteDB.From(sql)

    # Correct the query topoit the sqlite db
    if db and file(filexls):
        sql = sql.replace(filexls, "main")

    # Standard query
    try:
        cur = db.execute(sql, env, verbose=verbose)
        data = db.toObjects(cur)
        res = {"status": "success", "data": data, "exception": None}
        # Save only successfull queries---------------- ----------------------
        if not sql_stored and savequery:
            strtofile(sql, filesql)
            # -------------------------------------------------------------------
    except Exception, ex:
        res = {"status": "fail", "exception": "%s" % ex, "sql": sql}

    # anyway
    return JSONResponse(res, start_response)


if __name__ == '__main__':
    pass
