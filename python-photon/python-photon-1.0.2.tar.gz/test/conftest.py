# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2017 Cisco Systems, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

import pytest

from photon import config
from photon import provisioner


@pytest.fixture
def photon_config(request, photon_config_file):
    return config.Config(*request.param, config_file=photon_config_file)


@pytest.fixture
def photon_provisioner(photon_config_file):
    c = config.Config('test', 'upgrade', config_file=photon_config_file)
    return provisioner.Provisioner(c)


@pytest.fixture
def photon_config_content():
    return """
---
azs:
  test:
    inventory: az_inventory
    env:
      TEST_PHOTON_ENV: True
  test_invalid:
    inventory: az_invalid_inventory
workflows:
  upgrade:
    flags:
      - --become
    playbooks:
      - path: playbooks/openstack/metapod/package_upgrade.yml
        flags:
          - --extra-vars="skip_handlers=True"
          - --extra-vars="openstack_serial_controller=1"
          - --skip-tags="functional_tests,integration_tests"
      - path: playbooks/openstack/metapod/package_upgrade2.yml
    allowed_azs:
      - test
  restart:
    playbooks:
      - path: playbooks/openstack/metapod/restart.yml
"""


@pytest.fixture
def photon_config_file(photon_config_content, tmpdir, request):
    d = tmpdir.mkdir('photon')
    c = d.join(os.extsep.join(('photon', 'yml')))
    c.write(photon_config_content)

    def cleanup():
        os.remove(c.strpath)
        os.rmdir(d.strpath)

    request.addfinalizer(cleanup)

    return c.strpath
