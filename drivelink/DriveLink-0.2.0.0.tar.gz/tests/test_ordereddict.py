from drivelink import OrderedDict
import pytest
import os
#from Process import freeze_support


def test_dict():
    dct = OrderedDict("testOrderedDict")
    for i in range(10):
        dct[i] = i
    for i in range(10):
        assert dct[i] == i


def test_init():
    with pytest.raises(ValueError) as excinfo:
        OrderedDict("testOrderedDictInit", 0)
    excinfo.match(".* per page.*")
    with pytest.raises(ValueError) as excinfo:
        OrderedDict("testOrderedDictInit", 1, 0)
    excinfo.match(".* in RAM.*")
    with OrderedDict("testOrderedDictInit", 1, 1):
        pass
    OrderedDict("testOrderedDictInit", 1, 1)


def test_guarantee_page():
    with OrderedDict("testOrderedDictGuaranteePage", 1, 1) as d:
        d[0] = 1
        d[1] = "c"
        d[2] = 3.4
        assert d[0] == 1
        assert d[1] == "c"
        assert d[2] == 3.4


def test_string_funcs():
    d = OrderedDict("testOrderedDictStringFuncs")
    assert str(d).startswith("Dictionary")
    assert str(d).endswith("testOrderedDictStringFuncs")
    assert repr(d).startswith("OrderedDict(")
    assert repr(d).endswith(".DriveLink')")


def test_save():
    d = OrderedDict("testOrderedDictSave", 1, 1)
    d[0] = 1
    d[1] = "c"
    d[2] = 3.4
    d.close()
    with OrderedDict("testOrderedDictSave", 1, 1) as d:
        assert d[0] == 1
        assert d[1] == "c"
        assert d[2] == 3.4


if __name__ == '__main__':
    freeze_support()
    ut.main()
