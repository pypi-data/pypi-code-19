# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals


import json

import pytest

from netmagus.form import CheckBox, DropDownMenu, PasswordInput, RadioButton, TextArea, TextInput


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class TestNetMagusFormTextArea(object):
    @pytest.fixture(scope='class')
    def components(self):
        self.ta = TextArea(editable=True, label='My Label', description='My Description',
                           placeholder='My Placeholder', required=True)
        # sample form element as created in the NetMagus Form Designer UI
        self.ta_fd = json.loads('{"component": "textArea", "editable": true, "index": 0, "label": "My '
                                'Label", '
                                '"description": "My Description", "placeholder": "My Placeholder", '
                                '"options": [], '
                                '"required": true, "validation": "/.*/", "value": null}')
        return self

    def test_textarea_obj(self, components):
        assert components.ta.__dict__ == components.ta_fd

    def test_textarea_json(self, components):
        assert repr(components.ta) == json.dumps(components.ta_fd, sort_keys=True)
        assert json.dumps(components.ta.as_dict, sort_keys=True) == json.dumps(components.ta_fd, sort_keys=True)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class TestNetMagusFormTextInput(object):
    @pytest.fixture(scope='class')
    def components(self):
        self.ti = TextInput(editable=True, label='My Label',
                            description='My Description',
                            placeholder='My Placeholder', required=True,
                            validation='[number]')
        # sample form element as created in the NetMagus Form Designer UI
        self.ti_fd = json.loads(
                '{"component":"textInput","editable":true,"index":0,'
                '"label":"My '
                'Label",'
                '"description":"My Description","placeholder":"My Placeholder",'
                '"options":[],'
                '"required":true,"validation":"[number]", "value": null}')
        return self

    def test_textinput_json(self, components):
        assert repr(components.ti) == json.dumps(components.ti_fd,
                                                 sort_keys=True)

    def test_textinput_obj(self, components):
        assert components.ti.__dict__ == components.ti_fd
        assert json.dumps(components.ti.as_dict, sort_keys=True) == json.dumps(
                components.ti_fd, sort_keys=True)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class TestNetMagusFormCheckbox(object):
    @pytest.fixture(scope='class')
    def components(self):
        self.cb = CheckBox(editable=True, label='My Label',
                           description='My Description',
                           options=['Option 1', 'Option 2'], required=True,
                           value='test')

        self.cb_fd = json.loads(
                '{"component":"checkbox","editable":true,"index":0,"label":"My '
                'Label",'
                '"description":"My Description","placeholder":"","options":['
                '"Option 1","Option 2"],"required":true,"validation":"/.*/", '
                '"value":"test"}')
        return self

    def test_checkbox_json(self, components):
        assert repr(components.cb) == json.dumps(components.cb_fd,
                                                 sort_keys=True)

    def test_checkbox_obj(self, components):
        assert components.cb.__dict__ == components.cb_fd
        assert json.dumps(components.cb.as_dict, sort_keys=True) == json.dumps(
                components.cb_fd, sort_keys=True)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class TestNetMagusRadioButton(object):
    @pytest.fixture(scope='class')
    def components(self):
        self.rb = RadioButton(editable=True, label='My Label',
                              description='My Description',
                              options=['Option 1', 'Option 2'], value='test')

        self.rb_fd = json.loads(
                '{"component":"radio","editable":true,"index":0,"label":"My '
                'Label",'
                '"description":"My Description","placeholder":"","options":['
                '"Option 1","Option 2"],"required":false,"validation":"/.*/", '
                '"value":"test"}')
        return self

    def test_checkbox_json(self, components):
        assert repr(components.rb) == json.dumps(components.rb_fd,
                                                 sort_keys=True)

    def test_checkbox_obj(self, components):
        assert components.rb.__dict__ == components.rb_fd
        assert json.dumps(components.rb.as_dict, sort_keys=True) == json.dumps(
                components.rb_fd, sort_keys=True)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class TestNetMagusDropDownMenu(object):
    @pytest.fixture(scope='class')
    def components(self):
        self.dd = DropDownMenu(editable=True, label='My Label',
                               description='My Description',
                               options=['Option 1', 'Option 2'], value='test')

        self.dd_fd = json.loads('{"component":"select","description":"My '
                                'Description","editable":true,"index":0,'
                                '"label":"My Label","placeholder":"",'
                                '"options":["Option 1","Option 2"],'
                                '"required":false,"validation":"/.*/",'
                                '"value":"test"}')
        return self

    def test_dropdown_json(self, components):
        assert repr(components.dd) == json.dumps(components.dd_fd,
                                                 sort_keys=True)
        assert json.dumps(components.dd.as_dict, sort_keys=True) == json.dumps(
                components.dd_fd, sort_keys=True)

    def test_dropdown_obj(self, components):
        assert components.dd.__dict__ == components.dd_fd


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class TestNetMagusPasswordInput(object):
    @pytest.fixture(scope='class')
    def components(self):
        self.pi = PasswordInput(editable=True, label='My Label',
                                description='My Description',
                                placeholder='My Placeholder', required=True)

        self.pi_fd = json.loads(
                '{"component":"password","editable":true,"index":0,"label":"My '
                'Label",'
                '"description":"My Description","placeholder":"My Placeholder",'
                '"options":[],'
                '"required":true,"validation":"/.*/", "value": null}')
        return self

    def test_password_json(self, components):
        assert repr(components.pi) == json.dumps(components.pi_fd,
                                                 sort_keys=True)
        assert json.dumps(components.pi.as_dict, sort_keys=True) == json.dumps(
                components.pi_fd, sort_keys=True)

    def test_password_obj(self, components):
        assert components.pi.__dict__ == components.pi_fd
