
# -*- coding:utf-8 -*-

from terminal import bold, magenta
from ..util import list2table, client
from ..const import CMD



def list():

    print('%s' % bold(magenta('Instance types:')))
    list2table.print_table(client.list_instance_types() or [], [('name','Name'),('cpu','CPU(Core)'),('memory','Memory(GB)')],False)

    print('%s' % bold(magenta('Spot Instance types:')))
    list2table.print_table(client.list_spot_instance_types() or [],
                           [('name', 'Name'), ('cpu', 'CPU(Core)'), ('memory', 'Memory(GB)')], False)

    print('\n  using "%s set -t <Name>" to set default instance type\n' % (CMD))