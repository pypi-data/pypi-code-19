
#import ws_sheets_serve

import ws_sheets_server.tests.check_stored

def test(loop, addr_storage):
    ws_sheets_server.tests.check_stored.test(loop, addr_storage)

