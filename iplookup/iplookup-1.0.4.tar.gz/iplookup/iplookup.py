#!/usr/bin/env python
from dns.resolver import query as resolve

def iplookup(domains):
    '''
    This function is used to lookup all IP addresses assigned to a domain using DNS resolution.

    :param domains: single domain as a string, or multiple domains as a List type
    :return: Returns a List of IP Addresses from the domains supplied as Params
    '''
    # convert single string arg to single item list
    ip_list = []
    if isinstance(domains, str):
        domains = domains.split()
    elif not isinstance(domains, list):
        raise TypeError('iplookup only supports strings or lists') 

    for domain in domains:
        try:
            answer = resolve(domain)
        except Exception as e:
            print("Error occured doing lookup for {}".format(domain))
            break
        ip_list += [ str(ip.to_text()) for ip in answer if not ip == None ]
    return ip_list

