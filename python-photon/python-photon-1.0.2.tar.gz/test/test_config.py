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

import pytest

import photon
from photon import config


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_inventory(photon_config):
    assert 'az_inventory' == photon_config.inventory


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_env(photon_config):
    assert 'TEST_PHOTON_ENV' in photon_config.env


@pytest.mark.parametrize('photon_config', [['test', 'restart']], indirect=True)
def test_playbook_cmds(photon_config):
    assert ['playbooks/openstack/metapod/restart.yml', '-i',
            'az_inventory'] == photon_config.playbook_cmds[0]


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_working_workflow(photon_config):
    valid = photon_config.working_workflow['playbooks'][1]['path']
    assert len(photon_config.working_workflow['playbooks']) == 2
    assert 'playbooks/openstack/metapod/package_upgrade2.yml' == valid


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_get_allowed_azs(photon_config):
    assert ['test'] == photon_config._get_allowed_azs()


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_get_available_azs(photon_config):
    assert ['test',
            'test_invalid'] == sorted(photon_config._get_available_azs())


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_get_available_workflows(photon_config):
    assert ['restart',
            'upgrade'] == sorted(photon_config._get_available_workflows())


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_get_config(photon_config):
    assert 'azs' in photon_config._get_config()


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_workflow_allowed(photon_config):
    assert photon_config._get_workflow_allowed()


@pytest.mark.parametrize('photon_config', [['test', 'upgrade']], indirect=True)
def test_get_working_az(photon_config):
    assert 'az_inventory' == photon_config._get_working_az()['inventory']


# can't use photon_config fixture here since we need to catch an exception it
# raises during instantiation
def test_get_config_invalid(photon_config_file):
    with pytest.raises(photon.config.ConfigError):
        config.Config('test_invalid', 'upgrade', config_file='fake.yml')


def test_workflow_allowed_invalid(photon_config_file):
    with pytest.raises(photon.config.ConfigError):
        config.Config(
            'test_invalid', 'upgrade', config_file=photon_config_file)
