import sys
from qlib.net import to
from qlib.log import show
import json

def get_ip_information(ip, key):
    url='http://api.map.baidu.com/highacciploc/v1?qcip='+ip+'&qterm=pc&ak=' + key +'&coord=bd09ll&extensions=3'
    poiss=''
    request = to(url)
    page = request.json()
    
    if(page.has_key("content")):
        content=page["content"]
        address_component=content["address_component"]
        formatted_address=content["formatted_address"]
        show("geo :")
        show(address_component["country"])
        show(formatted_address)
        if (content.has_key("pois")):
            show("poi：")
            pois = content["pois"]
            for index in range(len(pois)):
                pois_name = pois[index]["name"]
                pois_address = pois[index]["address"]
                show(pois_name, pois_address)
    else:
        show('failed ')

if __name__ == '__main__':
    get_ip_information('183.55.116.95')