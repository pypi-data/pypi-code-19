#!/Anaconda3/python
# storytime

'''
description
'''


#----------------------------------------------------------------------#

def dprint( obj ) :
    """Custom pretty printer"""
    string = ""

    if hasattr(obj, "__dprint__"):
        string += obj.__dprint__

    elif isinstance( obj, list ):
        if len(obj) > 0:
            print("[" + str( obj.pop( 0 ) ), end='' )
            for element in obj :
                print("")
                print( ","+ str(element), end='' )
            print("]")
        else:
            print("[]")

    else:
        raise TypeError( "dprint requires __dprint__ attribute or list: " + str(obj) )

    print( string )
    return string


#----------------------------------------------------------------------#

def display( universe ) :
    pass


#----------------------------------------------------------------------#
