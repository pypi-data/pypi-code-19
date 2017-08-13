"""
test panflute ast to markdown conversion
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from .context import table2csv
from panflute import *


def test_table2csv():
    # get_table_body
    markdown = """| 1 | 2 | 3 | 4 |
|:--|--:|:-:|---|
| 1 | 2 | 3 | 4 |

: *abcd*
"""
    Panflute = convert_text(markdown)
    code_block_converted = table2csv(*Panflute, doc=None)
    code_block_referenced = CodeBlock('''---
alignment: LRCD
caption: '*abcd*'
header: true
markdown: true
table-width: 0
width: [0, 0, 0, 0]
---
1,2,3,4\r\n1,2,3,4\r\n''', classes=['table'])
    assert repr(code_block_converted) == repr(code_block_referenced)
    return
