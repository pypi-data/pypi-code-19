#
# -*- coding: utf-8 -*-

import codecs
import os

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


# TODO: Move the css to a .css file and read in!
CSS = u"""
<style>
pre {
	font-size:10px;
}
table a:link {
	color: #666;
	font-weight: bold;
	text-decoration:none;
}
table a:visited {
	color: #999999;
	font-weight:bold;
	text-decoration:none;
}
table a:active,
table a:hover {
	color: #bd5a35;
	text-decoration:underline;
}
table {
	font-family:Arial, Helvetica, sans-serif;
	font-weight:bold;
	color:#666;
	font-size:12px;
	background:#eaebec;
	margin:2px;
	border:#ccc 1px solid;

	-moz-border-radius:2px;
	-webkit-border-radius:2px;
	border-radius:2px;

	-moz-box-shadow: 0 1px 1px #d1d1d1;
	-webkit-box-shadow: 0 1px 1px #d1d1d1;
	box-shadow: 0 1px 1px #d1d1d1;
}
table th {
	border-top:1px solid #fafafa;
	border-bottom:1px solid #e0e0e0;

	background: #ededed;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
}
table th:first-child {
	text-align: center;
	padding:{padding};
}
table tr:first-child th:first-child {
	-moz-border-radius-topleft:2px;
	-webkit-border-top-left-radius:2px;
	border-top-left-radius:2px;
	padding:{padding};
}
table tr:first-child th:last-child {
	-moz-border-radius-topright:2px;
	-webkit-border-top-right-radius:2px;
	border-top-right-radius:2px;
	padding:{padding};
}
table tr {
	text-align: center;
	padding:{padding};
}
table td:first-child {
	text-align: left;
	border-left: 0;
	padding:{padding};
}
table td {
	border-top: 1px solid #ffffff;
	border-bottom:1px solid #e0e0e0;
	border-left: 1px solid #e0e0e0;

	padding:{padding};
	background: #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#fbfbfb), to(#fafafa));
	background: -moz-linear-gradient(top,  #fbfbfb,  #fafafa);
}
table tr.even td {
	background: #f6f6f6;
	background: -webkit-gradient(linear, left top, left bottom, from(#f8f8f8), to(#f6f6f6));
	background: -moz-linear-gradient(top,  #f8f8f8,  #f6f6f6);
}
table tr:last-child td {
	border-bottom:0;
}
table tr:last-child td:first-child {
	-moz-border-radius-bottomleft:2px;
	-webkit-border-bottom-left-radius:2px;
	border-bottom-left-radius:3px;
}
table tr:last-child td:last-child {
	-moz-border-radius-bottomright:2px;
	-webkit-border-bottom-right-radius:2px;
	border-bottom-right-radius:2px;
}
table tr:hover td {
	background: #f2f2f2;
	background: -webkit-gradient(linear, left top, left bottom, from(#f2f2f2), to(#f0f0f0));
	background: -moz-linear-gradient(top,  #f2f2f2,  #f0f0f0);
}

.tooltip {
	border-bottom: 1px dotted #000000; color: #000000; outline: none;
	cursor: help; text-decoration: none;
	position: relative;
}
.tooltip span {
	margin-left: -999em;
	position: absolute;
}
.tooltip:hover span {
	border-radius: 5px 5px; -moz-border-radius: 5px; -webkit-border-radius: 5px; 
	box-shadow: 5px 5px 5px rgba(0, 0, 0, 0.1); -webkit-box-shadow: 5px 5px rgba(0, 0, 0, 0.1); -moz-box-shadow: 5px 5px rgba(0, 0, 0, 0.1);
	font-family: Calibri, Tahoma, Geneva, sans-serif;
	position: absolute; left: 1em; top: 2em; z-index: 99;
	margin-left: 0; width: 250px;
}
.tooltip:hover em {
	font-family: Candara, Tahoma, Geneva, sans-serif; font-size: 1.2em; font-weight: bold;
	display: block; padding: 0.2em 0 0.6em 0;
}
.classic { padding: 0.8em 1em; }
.custom { padding: 0.5em 0.8em 0.8em 2em; }
* html a:hover { background: transparent; }
.classic {background: #FFFFAA; border: 1px solid #FFAD33; }
.critical { background: #FFCCAA; border: 1px solid #FF3334;	}
.help { background: #9FDAEE; border: 1px solid #2BB0D7;	}
.info { background: #9FDAEE; border: 1px solid #2BB0D7;	}
.warning { background: #FFFFAA; border: 1px solid #FFAD33; }
</style>
""".replace(u'{padding}', u'6px 15px 6px 15px')

OPEN_DOCUMENT_JS = u"""
<script>
    function open_document(text){
        window.open().document.write(text);
    }
</script>
"""

HEAD = (u'<!doctype html>\n'
        u'<html lang="en-GB">\n'
        u'<head>\n<meta charset="UTF-8">\n'
        u'{{css}}\n'
        + OPEN_DOCUMENT_JS
        + u'</head>\n')


def html_filename(html_folder = None,
                  filename = None):
    path = html_folder + os.sep if html_folder else u''
    return path + u'{filename}.html'.format(filename = unicode(filename) if filename else u'index')


def open(fname,
         css=CSS):

    f = codecs.open(fname,
                    u'w',
                    encoding=u'utf8')
    f.write(HEAD.replace(u'{{css}}', CSS))
    f.write(u'<body>\n')
    return f


def close(f):
    f.write(u'</body>\n'
            u'</html>')
    f.close()

