""" doc """
import pytest


class TestClass1(object):
    """ doc """
    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc001")
    def test_0001(self):
        """
        @Title: IDM-IPA-TC: test suite: test case 0001
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc002")
    def test_0002(self):
        """
        @Title: IDM-IPA-TC: test suite: test case 0002
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc003")
    def test_0003(self):
        """
        @Title: IDM-IPA-TC: test suite: test case 0003
        """
        pass

    def test_0004(self):
        """ IDM-IPA-TC: test suite: test case 0004 """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc004")
    def test_0005(self):
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc006")
    def test_0006(self):
        """
        :Title: IDM-IPA-TC: test suite: test case 0006
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc007")
    def test_0007(self):
        """
        :title: IDM-IPA-TC: test suite: test case 0007
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc008")
    def test_0008(self):
        """
        :Title :      IDM-IPA-TC: test suite: test case 0008
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc009")
    def test_0009(self):
        """
        :title   :    IDM-IPA-TC: test suite: test case 0009
        """
        pass
