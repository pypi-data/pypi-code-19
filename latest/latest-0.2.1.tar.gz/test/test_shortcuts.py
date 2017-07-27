import os.path
import pytest

from latest.shortcuts import *


@pytest.fixture
def template_file(res_dir):
    return os.path.join(res_dir, 'template.tmpl')


@pytest.fixture
def expected(res_dir):
    expected_file = os.path.join(res_dir, 'expected.tex')
    with open(expected_file, 'r') as f:
        return f.read()


def test_render(template_file, data_file, expected):
    (data_file, data_fmt) = data_file
    if data_fmt in ('yaml', 'yml'):
        try:
            import yaml
        except:
            assert True
            return
    assert render(template_file, data_file, data_fmt=data_fmt) == expected


