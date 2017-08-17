import os
import requests

def seussexport(data, username, password):

    try:

        requests.packages.urllib3.disable_warnings()
        headers = {'Accept':'application/json', 'Content-Type':'application/json'}

        url = (data['server']
            + '/api/latest/event/'
            + '?fields=device,description,status&status_formats=time,state'
            + '&description_filter==%27ping_state%27&status_filter==%27down%27&status_filter_format=state'
            + '&links=none'
            + '&limit=0')

        down_devices = requests.get(url, headers=headers, auth=(username, password), verify=False).json()

        skiplist = []
        for device in down_devices['data']['objects'][0]['data']:
            skiplist.append(device['device'])


        url = (data['server'] 
            + '/api/latest/cdt_device/?fields=' + ','.join(data['fields'])
            + '&filters=.snmp_poll_filter=IS(%27' + data['.snmp_poll_filter'] + '%27)'
            + '&.ping_poll_filter=IS(%27' + data['.ping_poll_filter'] + '%27)'
            + '&groups=' + ','.join(map(str,data['groups']))
            + '&limit=' + str(data['limit'])
            )
        devices = requests.get(url, headers=headers, auth=(username, password), verify=False).json()
        device_list = []

        for device in devices['data']['objects'][0]['data']:
            if device['SNMPv2-MIB.sysDescr']:
                if (any(x in device['SNMPv2-MIB.sysDescr'] for x in data['device_types']) and
                    not any(y in device['name'] for y in skiplist)):
                    tempdict = {}
                    tempdict['name'] = device['name']
                    tempdict['ipaddress'] = device['.ipaddress']
                    tempdict['vendor'] = device['SNMPv2-MIB.sysDescr'].split()[0]
                    device_list.append(tempdict)

        return device_list
    except Exception as e:
        pass
        return None