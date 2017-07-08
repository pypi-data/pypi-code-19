# -*- coding: utf-8 -*-

"""
Tools to parse a regular expression into nodes

:private:
"""

from typing import (
    Iterator,
    List)

from ..shared import (
    Node,
    OpNode,
    GroupNode,
    CharNode,
    Symbols,
    AlphaNumNode,
    DigitNode,
    SetNode,
    RepetitionRangeNode)


__all__ = [
    'parse',
    'fill_groups',
    'join_atoms']


SYMBOLS = {
    Symbols.JOINER: OpNode,
    Symbols.ZERO_OR_MORE: OpNode,
    Symbols.ZERO_OR_ONE: OpNode,
    Symbols.ONE_OR_MORE: OpNode,
    Symbols.OR: OpNode,
    Symbols.GROUP_START: GroupNode,
    Symbols.GROUP_END: GroupNode}


SHORTHANDS = {
    'w': AlphaNumNode,
    'd': DigitNode
}


def parse_set(set_expression: Iterator[str]) -> SetNode:
    """
    Parse a set atom (``[...]``) into a SetNode

    :param set_expression: content of a set (no brackets included)
    :return: a set node to match against (like any other char node)
    :private:
    """
    chars = []
    ranges = []
    shorthands = []
    is_range = False
    is_escaped = False

    for char in set_expression:
        if char == '\\' and not is_escaped:
            is_escaped = True
            continue

        if is_range:
            is_escaped = False
            is_range = False
            ranges.append(
                (chars.pop(), char))
            continue

        if char == '-' and not is_escaped and chars:
            is_range = True
            continue

        if is_escaped:
            is_escaped = False

            if char in SHORTHANDS:
                shorthands.append(
                    SHORTHANDS[char](char=char).char)
            else:
                chars.append(char)

            continue

        chars.append(char)

    assert not is_escaped
    assert chars or ranges or shorthands

    if is_range:
        chars.append('-')

    return SetNode(
        chars=chars,
        ranges=ranges,
        shorthands=shorthands)


def parse_repetition_range(range_expression):
    start = []
    end = []

    curr = start

    for char in range_expression:
        if char == ',':
            assert curr == start
            curr = end
            continue

        assert '0' <= char <= '9'
        curr.append(char)

    if curr == start:
        end = start

    start = int(''.join(start) or 0)

    if end:
        end = int(''.join(end))
    else:
        end = None

    return RepetitionRangeNode(
        char=Symbols.REPETITION_RANGE,
        start=start,
        end=end)


def parse(expression: str) -> Iterator[Node]:
    """
    Parse a regular expression into a sequence nodes.\
    Literals (escaped chars) are parsed as shorthands\
    (if found) or as regular char nodes.\
    Symbols (``*``, etc) are parsed into symbol nodes.\
    Same for groups. Sets are parsed into set nodes.

    :param expression: regular expression
    :return: iterator of nodes
    :private:
    """
    is_escaped = False

    is_set = False
    set_start = 0

    is_repetition_range = False
    repetition_range_tart = 0

    for index, char in enumerate(expression):
        if char == ']' and not is_escaped and set_start < index:
            assert is_set
            is_set = False
            yield parse_set(expression[set_start:index])
            continue

        if is_set:
            is_escaped = char == '\\' and not is_escaped
            continue

        if char == '[' and not is_escaped:
            assert not is_set
            is_set = True
            set_start = index + 1
            continue

        if char == '}' and not is_escaped:
            assert is_repetition_range
            is_repetition_range = False
            yield parse_repetition_range(expression[repetition_range_tart:index])
            continue

        if is_repetition_range:
            continue

        if char == '{' and not is_escaped:
            assert not is_repetition_range
            is_repetition_range = True
            repetition_range_tart = index + 1
            continue

        if is_escaped:
            is_escaped = False
            yield SHORTHANDS.get(char, CharNode)(char=char)
            continue

        if char == '\\':
            is_escaped = True
            continue

        yield SYMBOLS.get(char, CharNode)(char=char)

    assert not is_escaped
    assert not is_set
    assert not is_repetition_range


def fill_groups(nodes: List[Node]) -> int:
    """
    Fill groups with missing data.\
    This is index of group, whether\
    is a repeat group or not and capturing\
    flag for chars within the group

    This is required for later capturing of\
    characters when searching/matching a text

    :param nodes: a list of nodes
    :return: number of groups
    :private:
    """
    groups_count = 0
    groups = []

    for index, node in enumerate(nodes):
        if isinstance(node, CharNode):
            node.is_captured = bool(groups)
            continue

        if node.char == Symbols.GROUP_START:
            node.index = groups_count
            groups.append(node)
            groups_count += 1
            continue

        if node.char == Symbols.GROUP_END:
            try:
                next_node = nodes[index + 1]
            except IndexError:
                is_repeated = False
            else:
                is_repeated = next_node.char in (
                    Symbols.ZERO_OR_MORE,
                    Symbols.ONE_OR_MORE,
                    Symbols.REPETITION_RANGE)

            start = groups.pop()
            start.is_repeated = is_repeated

            node.index = start.index
            node.is_repeated = start.is_repeated

    assert not groups

    return groups_count


def join_atoms(nodes: Iterator[Node]) -> Iterator[Node]:
    """
    Add joiners to a sequence of nodes.\
    Joiners are meant to join sets\
    of chars that belong together.\
    This is required for later conversion into rpn notation.

    To clarify why this is necessary say there\
    is a math formula (not a regex) such as ``1+2``.\
    In RPN this would read as ``12+``.\
    Now what about ``11+12``? without joiners this would\
    read ``1112+`` and would be wrongly executed as ``111+2``.\
    Enter joins the RPN is ``1~11~2+`` and the parser\
    will know ``1~1`` means ``11`` and\
    ``1~2`` means ``12`` resulting in ``11+12``.

    Outputs::

        a~(b|c)*~d
        (a~b~c|d~f~g)
        a~b~c
        (a~b~c|d~e~f)*~x~y~z
        a+~b
        a?~b
        a*~b
        a+~b?
        (a)~(b)
        (a)~b

    :param nodes: a iterator of nodes
    :return: iterator of nodes containing joiners
    :private:
    """
    atoms_count = 0

    for node in nodes:
        if isinstance(node, CharNode):
            atoms_count += 1

            if atoms_count > 1:
                atoms_count = 1
                yield OpNode(char=Symbols.JOINER)

            yield node
            continue

        if node.char == Symbols.GROUP_START:
            if atoms_count:
                yield OpNode(char=Symbols.JOINER)

            atoms_count = 0
            yield node
            continue

        if node.char == Symbols.OR:
            atoms_count = 0
            yield node
            continue

        if node.char in {
                Symbols.GROUP_END,
                Symbols.ZERO_OR_MORE,
                Symbols.ONE_OR_MORE,
                Symbols.ZERO_OR_ONE,
                Symbols.REPETITION_RANGE}:
            atoms_count += 1
            yield node
            continue

        raise ValueError('Unhandled node %s' % repr(node))
