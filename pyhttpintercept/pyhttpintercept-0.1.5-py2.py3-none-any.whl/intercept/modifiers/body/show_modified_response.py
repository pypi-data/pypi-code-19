# encoding: utf-8

u"""
==================================================
If the calling handler can show a result,
this will force it to do so if there are
no other active modifiers.

No modification of the response is made.
--------------------------------------------------
Filter      : N/A
Override   : N/A
Parameters : N/A
==================================================
"""


def modify(request,
           response,
           parameters):

    # return the response unmodified.
    # The handler will assume a modification
    # has been made if the a modifier has been
    # called. This forces a call to
    # show_modified_response

    return response
