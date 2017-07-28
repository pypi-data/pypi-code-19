import json
import os
import time
from multiprocessing import Process
import requests
from requests.exceptions import (ConnectionError, ConnectTimeout)
from ..constants import power_status_list, power_status_action
from ..constants import (ACTION_POWER_ON, ACTION_POWER_OFF, ACTION_REBOOT)
from ..constants import (STATE_UNKNOWN, STATE_POWER_ON, STATE_POWER_OFF,
    STATE_POWERING_ON, STATE_POWERING_OFF)
from .boot_order import boot_order_priority, setting_boot_type
from ..exceptions import *


POWER_ACTION_TIMEOUT = 600  # 10 minutes

requests.packages.urllib3.disable_warnings()


class Client(object):
    def __init__(self, username=None, password=None,
                 version=None, ip='127.0.0.1', port=443):

        self._version = version
        self._username = username
        self._password = password
        self._url = 'https://%s' % ip

    def _gen_node_action_url(self, node_id):
        return '{url}/node/{node_id}'.format(url=self._url, node_id=node_id)

    def _get_node_details(self, node_id):
        url = self._gen_node_action_url(node_id)
        try:
            r = requests.get(url,
                             auth=(self._username, self._password),
                             verify=False,
                             timeout=(10, 10))
            result = {
                'status_code': r.status_code,
                'encoding': r.encoding,
                'headers': r.headers,
                'body': r.json()
            }
            return result
        except ConnectionError or ConnectTimeout as ex:
            raise ConnectionFailureException(node_id=node_id, detail=str(ex))
        except Exception as ex:
            raise NodeDetailsException(message=str(ex), node_id=node_id)

    def get_node_status(self, node_id):
        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            return response['body']['accessState'].lower()
        else:
            return 'unknown'

    def get_node_info(self, node_id):
        response = self._get_node_details(node_id)
        info = {}
        if response['status_code'] == 200:
            body = response['body']
            info['uuid'] = body.get('uuid', None)
            info['name'] = body.get('hostname', 'Unknown')
            info['power_state'] = power_status_list.get(
                body.get('powerStatus', 0), 0)

            info['chassis_id'] = None  # nullable
            info['target_power_state'] = None  # nullable
            info['provision_state'] = None   # nullable
            info['target_provision_state'] = None  # nullable
            info['provision_updated_at'] = None  # nullable
            info['last_error'] = None  # nullable
            info['instance_uuid'] = None  # nullable
            info['instance_info'] = None  # nullable

            info['raid_config'] = body.get('raidSettings', [])  # An array
            info['target_raid_config'] = []
            info['maintenance'] = False \
                if body.get('accessState', 'unknown') == 'online' else True
            info['maintenance_reason'] = None  # nullable
            info['console_enabled'] = False  # False is by default, what's this
            info['extra'] = {}  # What's this?
            info['properties'] = {}  # What's this?
        else:
            err_msg = "Fail to get node info, http status code is %s, " \
                      "http response is %s" % (response['status_code'], response['body'])
            raise NodeDetailsException(node_id=node_id, detail=err_msg)

        return info

    def _gen_power_action_file_path(self, node_id, action):
        file_name = "{action}_{node_id}_in_progress".format(action=action, node_id=node_id)
        pre_path = "/tmp" if os.path.exists("/tmp") else "./"  # resolve Windows OS problem
        path = os.path.join(pre_path, file_name)
        return path

    def _check_power_action_running(self, node_id):
        power_on_file = self._gen_power_action_file_path(node_id, ACTION_POWER_ON)
        power_off_file = self._gen_power_action_file_path(node_id, ACTION_POWER_OFF)

        if os.path.exists(power_on_file) and os.path.exists(power_off_file):
            now = time.time()
            delta_on = now - os.path.getmtime(power_on_file)
            delta_off = now - os.path.getmtime(power_off_file)

            if (delta_on > POWER_ACTION_TIMEOUT and delta_off > POWER_ACTION_TIMEOUT) or \
               (delta_on <= POWER_ACTION_TIMEOUT and delta_off <= POWER_ACTION_TIMEOUT):
                os.remove(power_on_file)
                os.remove(power_off_file)
                result = None
            elif delta_on > POWER_ACTION_TIMEOUT:
                os.remove(power_on_file)
                result = STATE_POWER_OFF
            elif delta_off > POWER_ACTION_TIMEOUT:
                os.remove(power_off_file)
                result = STATE_POWER_ON

        elif os.path.exists(power_on_file):
            delta = time.time() - os.path.getmtime(power_on_file)
            if delta > POWER_ACTION_TIMEOUT:
                os.remove(power_on_file)
                result = None
            else:
                result = STATE_POWERING_ON

        elif os.path.exists(power_off_file):
            delta = time.time() - os.path.getmtime(power_off_file)
            if delta > POWER_ACTION_TIMEOUT:
                os.remove(power_off_file)
                result = None
            else:
                result = STATE_POWERING_OFF

        else:
            result = None

        return result

    def get_node_power_status(self, node_id):
        result = self._check_power_action_running(node_id)
        if result:
            return result

        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            result = power_status_list[response['body']['powerStatus']]
        else:
            result = STATE_UNKNOWN
        return result

    def _set_power_status(self, node_id, action):
        url = self._gen_node_action_url(node_id)
        data = {'powerState': action}
        try:
            power_action_file = self._gen_power_action_file_path(node_id, action)
            out_file = open(power_action_file, "w")
            out_file.close()

            requests.put(url,
                         auth=(self._username, self._password),
                         data=json.dumps(data),
                         verify=False)
        except ConnectionError or ConnectTimeout as ex:
            raise ConnectionFailureException(node_id=node_id, detail=str(ex))
        finally:
            if os.path.exists(power_action_file):
                os.remove(power_action_file)

    def set_node_power_status(self, node_id, action):
        if action not in power_status_action:
            raise BadPowerStatusSettingException(action=action)
        action = power_status_action[action]

        p = Process(target=self._set_power_status, args=(node_id, action))
        p.start()

    def get_node_all_boot_info(self, node_id):
        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            return {'bootOrder': response['body']['bootOrder']}

    def get_node_boot_info(self, node_id):
        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            boot_order_list = response['body']['bootOrder']['bootOrderList']

            for boot_order in boot_order_list:
                type_name = boot_order['bootType'].lower()
                for item in boot_order_priority:
                    if item['name'] == type_name:
                        item['value'] = boot_order

            final_boot_order = None
            for item in boot_order_priority:
                if item['value'] is not None:
                    final_boot_order = item['value']
                    break

            return final_boot_order

        else:
            return None

    def set_node_boot_info(self, node_id, boot_order):
        # for item in boot_order['bootOrder']['bootOrderList']:
        #     if item['bootType'] in setting_boot_type:
        #         item['bootType'] = setting_boot_type[item['bootType']]

        try:
            url = self._gen_node_action_url(node_id)
            r = requests.put(url,
                             auth=(self._username, self._password),
                             data=json.dumps(boot_order),
                             verify=False)
            if r.status_code != 200:
                raise Exception("Fail to set node boot info. status code = %s" % r.status_code)
        except ConnectionError or ConnectTimeout as ex:
            raise ConnectionFailureException(node_id=node_id, detail=str(ex))
        except Exception as ex:
            print("Exception! - %s" % str(ex))

    def ready_for_deployment(self, node_id):
        response = self._get_node_details(node_id)
        result = False
        if response['status_code'] == 200:
            power_status = power_status_list[response['body']['powerStatus']]
            if power_status in ['on', 'off']:
                result = True
        return result
