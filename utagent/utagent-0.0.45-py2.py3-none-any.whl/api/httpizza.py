#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from slave.config import (
    config,
    environment
)


def post_agent(ip, port, name):
    try:
        print(environment[config["environment"]])
        url = environment[config["environment"]] + 'agent'
        print(url)
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
        print(e)


def post_device(ip, brand, model, os_version, rom_version, device_id):
    url = environment[config["environment"]] + 'device'
    info = {
        'ip': ip,
        'brand': brand,
        'model': model,
        'os_version': os_version,
        'rom_version': rom_version,
        'device_id': device_id
    }
    r = requests.post(url, json=info)
    if r.ok:
        return True
    else:
        return False
