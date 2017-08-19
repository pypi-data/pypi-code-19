import pytest


@pytest.fixture
def img():
    from s1acker.s1acker import Img
    return Img(
        "http://nosuchurl.com/nosuchpic.jpg",
        "test",
        origin="http://bbs.saraba1st.com/2b/thread-424242-1-1.html"
    )


def test_attr(img):
    assert img._topic == '424242'
    assert img._fmt == '.jpg'
    assert img._name == 'test'
    assert img._url == "http://nosuchurl.com/nosuchpic.jpg"


def test_repr(img):
    assert repr(img) == '![test.jpg](http://nosuchurl.com/nosuchpic.jpg)'
    assert repr(img) == str(img)
