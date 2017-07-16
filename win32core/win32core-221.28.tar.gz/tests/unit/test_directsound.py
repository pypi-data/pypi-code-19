import pytest
import pytest

from directsound import *


def test_DSBCAPS():
    DSBCAPS()


def test_DSBUFFERDESC():
    DSBUFFERDESC()


def test_DSCAPS():
    DSCAPS()


def test_DSCBCAPS():
    DSCBCAPS()


def test_DSCBUFFERDESC():
    DSCBUFFERDESC()


def test_DSCCAPS():
    DSCCAPS()


@pytest.mark.skip
def test_DirectSoundCaptureCreate():
    DirectSoundCaptureCreate()


def test_DirectSoundCaptureEnumerate():
    DirectSoundCaptureEnumerate()


@pytest.mark.xfail
def test_DirectSoundCreate():
    DirectSoundCreate()


def test_DirectSoundEnumerate():
    DirectSoundEnumerate()
