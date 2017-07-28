
# -*- coding:utf-8 -*-

from terminal import bold, magenta
from ..util import list2table, client


def list():
    # system disk types
    arr = client.get_quotas().AvailableClusterResourceType
    t = []
    for n in arr:
        t.append({'name':n})

    print('%s' % bold(magenta('Resource Types:')))
    list2table.print_table(t, [('name', 'Name')], False)