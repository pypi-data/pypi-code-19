#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import logging

logger = logging.getLogger(__name__)

qualityplatform_api_url = "http://qp.alpha.elenet.me/api/"


def add_agent(ip, port, name):
    try:
        url = qualityplatform_api_url + 'agent'
        info = {
            'ip': ip,
            'port': port,
            'name': name
        }
        r = requests.post(url, json=info)
        if r.ok:
            return True
        else:
            return False
    except requests.RequestException as e:
        logger.exception(e)


def update_device_status(device_ip, status):
    try:
        url = qualityplatform_api_url + 'device/status'
        info = {
            'device_ip': device_ip,
            'status': status
        }
        r = requests.put(url, json=info)
        if r.ok:
            return True
        else:
            return False
    except requests.RequestException as e:
        logger.exception(e)


def add_case_file(name, app_version_id, module_id, file_hash):
    try:
        url = qualityplatform_api_url + 'testcase'
        info = {
            'name': name,
            'description': '',
            'test_type': 1,
            'app_version_id': app_version_id,
            'module_id': module_id,
            'fuss_hash': file_hash,
        }
        r = requests.post(url, json=info)
        if r.ok:
            return True
        else:
            return False
    except requests.RequestException as e:
        logger.exception(e)


def upload_case_file(name, app_version_id, module_id, case_file):
    try:
        url = qualityplatform_api_url + 'file/upload'
        info = {
            'file_to_upload': case_file
        }
        r = requests.post(url, data=info)
        if r.ok:
            add_case_file(name, app_version_id, module_id, r.text)
            return True
        else:
            return False
    except requests.RequestException as e:
        logger.exception(e)
