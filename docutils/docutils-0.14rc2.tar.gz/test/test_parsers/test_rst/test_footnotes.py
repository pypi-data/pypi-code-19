#! /usr/bin/env python

# $Id: test_footnotes.py 4564 2006-05-21 20:44:42Z wiemann $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Tests for states.py.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['footnotes'] = [
["""\
.. [1] This is a footnote.
""",
"""\
<document source="test data">
    <footnote ids="id1" names="1">
        <label>
            1
        <paragraph>
            This is a footnote.
"""],
["""\
.. [1] This is a footnote
   on multiple lines.
""",
"""\
<document source="test data">
    <footnote ids="id1" names="1">
        <label>
            1
        <paragraph>
            This is a footnote
            on multiple lines.
"""],
["""\
.. [1] This is a footnote
     on multiple lines with more space.

.. [2] This is a footnote
  on multiple lines with less space.
""",
"""\
<document source="test data">
    <footnote ids="id1" names="1">
        <label>
            1
        <paragraph>
            This is a footnote
            on multiple lines with more space.
    <footnote ids="id2" names="2">
        <label>
            2
        <paragraph>
            This is a footnote
            on multiple lines with less space.
"""],
["""\
.. [1]
   This is a footnote on multiple lines
   whose block starts on line 2.
""",
"""\
<document source="test data">
    <footnote ids="id1" names="1">
        <label>
            1
        <paragraph>
            This is a footnote on multiple lines
            whose block starts on line 2.
"""],
["""\
.. [1]

That was an empty footnote.
""",
"""\
<document source="test data">
    <footnote ids="id1" names="1">
        <label>
            1
    <paragraph>
        That was an empty footnote.
"""],
["""\
.. [1]
No blank line.
""",
"""\
<document source="test data">
    <footnote ids="id1" names="1">
        <label>
            1
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent.
    <paragraph>
        No blank line.
"""],
]

totest['auto_numbered_footnotes'] = [
["""\
[#]_ is the first auto-numbered footnote reference.
[#]_ is the second auto-numbered footnote reference.

.. [#] Auto-numbered footnote 1.
.. [#] Auto-numbered footnote 2.
.. [#] Auto-numbered footnote 3.

[#]_ is the third auto-numbered footnote reference.
""",
"""\
<document source="test data">
    <paragraph>
        <footnote_reference auto="1" ids="id1">
         is the first auto-numbered footnote reference.
        <footnote_reference auto="1" ids="id2">
         is the second auto-numbered footnote reference.
    <footnote auto="1" ids="id3">
        <paragraph>
            Auto-numbered footnote 1.
    <footnote auto="1" ids="id4">
        <paragraph>
            Auto-numbered footnote 2.
    <footnote auto="1" ids="id5">
        <paragraph>
            Auto-numbered footnote 3.
    <paragraph>
        <footnote_reference auto="1" ids="id6">
         is the third auto-numbered footnote reference.
"""],
["""\
[#third]_ is a reference to the third auto-numbered footnote.

.. [#first] First auto-numbered footnote.
.. [#second] Second auto-numbered footnote.
.. [#third] Third auto-numbered footnote.

[#second]_ is a reference to the second auto-numbered footnote.
[#first]_ is a reference to the first auto-numbered footnote.
[#third]_ is another reference to the third auto-numbered footnote.

Here are some internal cross-references to the targets generated by
the footnotes: first_, second_, third_.
""",
"""\
<document source="test data">
    <paragraph>
        <footnote_reference auto="1" ids="id1" refname="third">
         is a reference to the third auto-numbered footnote.
    <footnote auto="1" ids="first" names="first">
        <paragraph>
            First auto-numbered footnote.
    <footnote auto="1" ids="second" names="second">
        <paragraph>
            Second auto-numbered footnote.
    <footnote auto="1" ids="third" names="third">
        <paragraph>
            Third auto-numbered footnote.
    <paragraph>
        <footnote_reference auto="1" ids="id2" refname="second">
         is a reference to the second auto-numbered footnote.
        <footnote_reference auto="1" ids="id3" refname="first">
         is a reference to the first auto-numbered footnote.
        <footnote_reference auto="1" ids="id4" refname="third">
         is another reference to the third auto-numbered footnote.
    <paragraph>
        Here are some internal cross-references to the targets generated by
        the footnotes: \n\
        <reference name="first" refname="first">
            first
        , \n\
        <reference name="second" refname="second">
            second
        , \n\
        <reference name="third" refname="third">
            third
        .
"""],
["""\
Mixed anonymous and labelled auto-numbered footnotes:

[#four]_ should be 4, [#]_ should be 1,
[#]_ should be 3, [#]_ is one too many,
[#two]_ should be 2, and [#six]_ doesn't exist.

.. [#] Auto-numbered footnote 1.
.. [#two] Auto-numbered footnote 2.
.. [#] Auto-numbered footnote 3.
.. [#four] Auto-numbered footnote 4.
.. [#five] Auto-numbered footnote 5.
.. [#five] Auto-numbered footnote 5 again (duplicate).
""",
"""\
<document source="test data">
    <paragraph>
        Mixed anonymous and labelled auto-numbered footnotes:
    <paragraph>
        <footnote_reference auto="1" ids="id1" refname="four">
         should be 4, \n\
        <footnote_reference auto="1" ids="id2">
         should be 1,
        <footnote_reference auto="1" ids="id3">
         should be 3, \n\
        <footnote_reference auto="1" ids="id4">
         is one too many,
        <footnote_reference auto="1" ids="id5" refname="two">
         should be 2, and \n\
        <footnote_reference auto="1" ids="id6" refname="six">
         doesn't exist.
    <footnote auto="1" ids="id7">
        <paragraph>
            Auto-numbered footnote 1.
    <footnote auto="1" ids="two" names="two">
        <paragraph>
            Auto-numbered footnote 2.
    <footnote auto="1" ids="id8">
        <paragraph>
            Auto-numbered footnote 3.
    <footnote auto="1" ids="four" names="four">
        <paragraph>
            Auto-numbered footnote 4.
    <footnote auto="1" dupnames="five" ids="five">
        <paragraph>
            Auto-numbered footnote 5.
    <footnote auto="1" dupnames="five" ids="id9">
        <system_message backrefs="id9" level="2" line="12" source="test data" type="WARNING">
            <paragraph>
                Duplicate explicit target name: "five".
        <paragraph>
            Auto-numbered footnote 5 again (duplicate).
"""],
["""\
Mixed manually-numbered, anonymous auto-numbered,
and labelled auto-numbered footnotes:

[#four]_ should be 4, [#]_ should be 2,
[1]_ is 1, [3]_ is 3,
[#]_ should be 6, [#]_ is one too many,
[#five]_ should be 5, and [#six]_ doesn't exist.

.. [1] Manually-numbered footnote 1.
.. [#] Auto-numbered footnote 2.
.. [#four] Auto-numbered footnote 4.
.. [3] Manually-numbered footnote 3
.. [#five] Auto-numbered footnote 5.
.. [#five] Auto-numbered footnote 5 again (duplicate).
.. [#] Auto-numbered footnote 6.
""",
"""\
<document source="test data">
    <paragraph>
        Mixed manually-numbered, anonymous auto-numbered,
        and labelled auto-numbered footnotes:
    <paragraph>
        <footnote_reference auto="1" ids="id1" refname="four">
         should be 4, \n\
        <footnote_reference auto="1" ids="id2">
         should be 2,
        <footnote_reference ids="id3" refname="1">
            1
         is 1, \n\
        <footnote_reference ids="id4" refname="3">
            3
         is 3,
        <footnote_reference auto="1" ids="id5">
         should be 6, \n\
        <footnote_reference auto="1" ids="id6">
         is one too many,
        <footnote_reference auto="1" ids="id7" refname="five">
         should be 5, and \n\
        <footnote_reference auto="1" ids="id8" refname="six">
         doesn't exist.
    <footnote ids="id9" names="1">
        <label>
            1
        <paragraph>
            Manually-numbered footnote 1.
    <footnote auto="1" ids="id10">
        <paragraph>
            Auto-numbered footnote 2.
    <footnote auto="1" ids="four" names="four">
        <paragraph>
            Auto-numbered footnote 4.
    <footnote ids="id11" names="3">
        <label>
            3
        <paragraph>
            Manually-numbered footnote 3
    <footnote auto="1" dupnames="five" ids="five">
        <paragraph>
            Auto-numbered footnote 5.
    <footnote auto="1" dupnames="five" ids="id12">
        <system_message backrefs="id12" level="2" line="14" source="test data" type="WARNING">
            <paragraph>
                Duplicate explicit target name: "five".
        <paragraph>
            Auto-numbered footnote 5 again (duplicate).
    <footnote auto="1" ids="id13">
        <paragraph>
            Auto-numbered footnote 6.
"""],
]

totest['auto_symbol_footnotes'] = [
["""\
.. [*] This is an auto-symbol footnote.
""",
"""\
<document source="test data">
    <footnote auto="*" ids="id1">
        <paragraph>
            This is an auto-symbol footnote.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
