# -*- coding: utf-8 -*-

import pytest

from s1acker.cli import parse_args


class TestParseArgs(object):
    """Test parse_args()"""

    def test_doc(self):
        with pytest.raises(SystemExit) as e:
            parse_args(["-h"])
        assert e.value.code == 0

    def test_empty(self):
        with pytest.raises(SystemExit) as e:
            parse_args([])
        assert e.value.code == 2

    def test_unrec(self):
        with pytest.raises(SystemExit) as e:
            parse_args(["arg1", "--NOSUCHFLAG"])
        assert e.value.code == 2

    def test_srchtxt_single(self):
        args = parse_args(["hello"])
        assert args['srchtxt'] == 'hello' and args['srchuname'] is None

    def test_srchtxt_single_uname(self):
        args = parse_args(["hello", "-n", "world"])
        assert args['srchtxt'] == 'hello' and args['srchuname'] == 'world'

    def test_srchtxt_mulitple(self):
        args = parse_args([
            "the", "answer", "to", "everything", "--srchuname", "world"
        ])
        assert (
            args['srchtxt'] == 'the answer to everything'
            and args['srchuname'] == 'world'
        )
