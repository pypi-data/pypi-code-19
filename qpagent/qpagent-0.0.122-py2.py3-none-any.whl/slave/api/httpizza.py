#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from agent.config import config
import logging

logger = logging.getLogger(__name__)


def add_agent(ip, port, name):
    try:
        url = config["environment"] + 'agent'
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
        url = config["environment"] + 'device/status'
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


def upload_case_file(case_file):
    try:
        url = config["environment"] + 'file/upload'
        info = {
            'file_to_upload': case_file
        }
        r = requests.post(url, data=info)
        if r.ok:
            return True
        else:
            return False
    except requests.RequestException as e:
        logger.exception(e)
