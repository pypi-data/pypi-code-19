# -*- coding: utf-8 -*-

#  goma
#  ----
#  Generic object mapping algorithm.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/goma
#  License: APACHE Version 2 License (see LICENSE file)


class BaseMatch(object):
    """ Base match class """

    def match(self, *args):
        """ return match results """
        pass  # functions are implemented in sub classes

    def _has_relation_operator(self, condition_str):
        return str(condition_str)[:1] in ['<', '>', '!', '=', '(', '[']

    def _apply_relation_match(self, match_value, detail_value):
        """ return relation match results """

        match_value = match_value.replace(' ', '')

        # if interval
        if match_value[:1] in ['[', '(']:
            rel_vals = [type(detail_value)(val) for val in match_value[1:-1].split(',')]
            rel_ops = [self._repl_relation_operator(op) for op in [match_value[0], match_value[-1]]]
            # fixme NO eval usage !!!
            match_res = eval(
                'detail_value ' + rel_ops[0] + ' rel_vals[0] and detail_value ' + rel_ops[1] + ' rel_vals[1]')
        # else
        else:
            if self._repl_relation_operator(match_value[:2]):
                rel_ops = match_value[:2]
                rel_val = type(detail_value)(match_value[2:])
            else:
                rel_ops = match_value[:1]
                rel_val = type(detail_value)(match_value[1:])

            match_res = eval('detail_value ' + rel_ops + ' rel_val')

        return match_res

    def _repl_relation_operator(self, relation_symbol):
        if relation_symbol == '[': return '>='
        if relation_symbol == '(': return '>'
        if relation_symbol == ']': return '<='
        if relation_symbol == ')': return '<'
        if relation_symbol in ['<=', '=<']: return '<='
        if relation_symbol in ['>=', '=>']: return '>='
        if relation_symbol == '==': return '=='
        if relation_symbol == '!=': return '!='
        return relation_symbol
