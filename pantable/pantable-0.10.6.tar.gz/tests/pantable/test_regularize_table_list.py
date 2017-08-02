"""

"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from .context import regularize_table_list


def test_regularize_table_list():
    raw_table_list = [['1'], ['2', '3', '4', '5', '6', '7']]
    table_list, number_of_columns = regularize_table_list(raw_table_list)
    assert table_list == [
        ['1', '', '', '', '', ''],
        ['2', '3', '4', '5', '6', '7']
    ]
    assert number_of_columns == 6
    return
