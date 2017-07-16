
'''
evaluate yamlisp s-expressions
'''

from pathlib import Path
from . import functions

import logging
log = logging.getLogger( name="yamlisp.eval" )
log.debug = lambda *a, **b : None
# log.debug = print

#----------------------------------------------------------------------#

def _eval_yamlisp_path( current_config, target_config, target_data, target_section_name, target_key, target_path: Path ) :
    result = None
    return result


#----------------------------------------------------------------------#

def _eval_yamlisp_list( current_config, target_config, target_data, target_section_name, target_key, s_expression: list ) :
    key    = s_expression[0].strip('~')
    args   = s_expression[1:]

    if key[0] == "^": ### leading caret causes deferal of execution of a statement
        log.debug("!!!!DEFERRAL!!!!")
        return [key[1:], *args]
    else:
        log.debug("!!!!FUNCCALL!!!!")
        try:
            return functions.__dict__["_"+key]( current_config, target_config, target_data, target_section_name, target_key, s_expression)
        except KeyError:
            return s_expression


#----------------------------------------------------------------------#

def _eval_yamlisp_dict( current_config, target_config, target_data, target_section_name, target_key, s_expression: dict ) :
    result = None
    return result


#----------------------------------------------------------------------#

def eval_yamlisp( current_config, target_config, target_data, target_section_name, target_key, s_expression ) -> str :
    if isinstance( s_expression, dict ) :
        log.debug( "!!!!DICT!!!!" )
        return _eval_yamlisp_dict( current_config, target_config, target_data, target_section_name, target_key, s_expression )

    elif isinstance( s_expression, functions.PathList ):
        return s_expression

    elif isinstance( s_expression, list ) :
        log.debug( "!!!!LIST!!!!", s_expression, target_section_name, target_key )
        return _eval_yamlisp_list( current_config, target_config, target_data, target_section_name, target_key, s_expression )

    else :
        log.debug("!!!!ELSE!!!!")
        return str( s_expression )


#----------------------------------------------------------------------#
