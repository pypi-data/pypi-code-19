import CloudFlare
import json
import string
import re
from optparse import OptionParser
import traceback
import sys

from dns import resolver


import os


class Cloudflare:
    def __init__(self):
        if 'CLOUDFLARE_DOMAIN' in os.environ:
            self.domain = os.environ['CLOUDFLARE_DOMAIN']
        else:
            self.domain = os.environ['CLOUDFLARE_EMAIL'].split("@")[1]

        self.cf = CloudFlare.CloudFlare(email=os.environ['CLOUDFLARE_EMAIL'],
                                        token=os.environ['CLOUDFLARE_API'],
                                        raw=True)
        self.zone_id = self.get_zone_id()

    def get_zone_id(self):
        # query for the zone name and expect only one value back
        try:
            raw_results = self.cf.zones.get(params = {'name': self.domain, 'per_page': 1})
            zones = raw_results['result']
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            traceback.print_exc(file=sys.stdout)
            exit('/zones.get/%s %d %s - api call failed' % (self.domain,e, e))
        except Exception as e:
            exit('/zones.get/%s - %s - api call failed' % (self.domain,e))

        if len(zones) == 0:
            exit('No zones found')

        # extract the zone_id which is needed to process that zone
        zone = zones[0]
        return zone['id']


    def list(self):
        page_number = 0
        records = {}
        while True:
            # request the DNS records from that zone
            try:
                raw_dns_results = self.cf.zones.dns_records.get(self.zone_id, params={'per_page': 100, 'page': page_number})
                dns_records = raw_dns_results['result']
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.get %d %s - api call failed' % (e, e))
            for rec in dns_records:
                try:
                    records[rec['name']] = rec
                except Exception, e:
                    print str(e)

            total_pages = raw_dns_results['result_info']['total_pages']
            page_number += 1
            if page_number > total_pages:
                break
        return records


    def list_srv(self, dns):
       _resolver = resolver.Resolver()
       _resolver.nameservers = [resolver.query('beth.ns.cloudflare.com', 'A')[0].address]
       list=[]
       for srv in _resolver.query(dns, 'SRV'):
          host = str(srv.target)
          if host.endswith('.'):
            list.append(host[0:-1])
          else:
            list.append(host)
       return list


    def find(self, host):
        hosts = self.list()
        for rec in hosts:
            try:
                if host == rec:
                    return {
                        "id": hosts[rec]['id'],
                        "name": hosts[rec]['name'],
                        "ip": hosts[rec]['content'],
                        "zone_id": hosts[rec]['zone_id']
                    }
            except Exception, e:
                print str(e)


    def is_valid_ip(self, ip):
        m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
        return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))


    def append_entry(self, zone, value, type='SRV'):
        if self.domain != None and self.domain not in zone:
            host = "%s.%s" % (host, self.domain)
        domain = string.join(zone.split('.')[1:], '.')
        srv = zone.split('.')[0]
        data={'type': type, 'name': zone, 'content': value,"data":{"priority":0,"weight":0,"port":80,"target":value,"service":srv,"proto":"_tcp","name":domain}}
        print json.dumps(self.cf.zones.dns_records.post(self.zone_id, data=data), indent=5)


    def create_entry(self, ip, host):
        if self.domain != None and self.domain not in host:
            host = "%s.%s" % (host, self.domain)
        print "Looking up %s" % host
        record = self.find(host)
        if record is None:
            print "adding ip %s -> %s" % (ip, host)
            try:
                if self.is_valid_ip(ip):
                    raw_dns_results = self.cf.zones.dns_records.post(self.zone_id,
                                    data = {'type':'A', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)
                else:
                    raw_dns_results = self.cf.zones.dns_records.post(self.zone_id,
                                    data = {'type':'CNAME', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.post %d %s - api call failed' % (e, e))
        else:
            try:
                if self.is_valid_ip(ip):
                    print "updating ip %s -> %s" % (ip, host)
                    raw_dns_results = self.cf.zones.dns_records.put(record['zone_id'], record['id'],
                                    data = {'id': record['id'], 'type':'A', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)
                else:
                    print "updating cname %s -> %s" % (ip, host)
                    raw_dns_results = self.cf.zones.dns_records.put(record['zone_id'],record['id'],
                                    data = {'id': record['id'],'type':'CNAME', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)

            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.put %d %s - api call failed' % (e, e))


    def delete_entry(self, host):
        if self.domain != None and self.domain not in host:
            host = "%s.%s" % (host, self.domain)
        print "Looking up %s" % host
        record = self.find(host)
        if record is None:
            print "Record not found"
            exit(1)
        else:
            print "deleting %s" % (host)
            try:
                raw_dns_results = self.cf.zones.dns_records.delete(record['zone_id'], record['id'])
                print json.dumps(raw_dns_results, indent=5)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.put %d %s - api call failed' % (e, e))


def main():
    parser = OptionParser()
    parser.add_option(

        "-i", "--ip", dest="ip", help="The IP address of the instance to use")

    parser.add_option("-l", "--list", dest="list", help="List all entries")
    parser.add_option("-s", "--srv", dest="services", action="store_true", help="List all SRV entries for a doma")
    parser.add_option("-d", "--dns", dest="dns", help="A dns hostname to name")
    parser.add_option("-p", "--append", dest="append", action="store_true",  help="Append, don't replace the value")

    parser.add_option("--ips", dest="ips", action="store_true",  help="List all cloudflare IP's")
    parser.add_option("--del", dest="del_ent", action="store_true",  help="Delete cloudflare entry")
    (options, args) = parser.parse_args()


    if (options.list):
        hosts = Cloudflare().list()
        for host in hosts:
            print "%s = %s" % (host, hosts[host]['content'])
    elif (options.ips):
        hosts = Cloudflare().list()
        for host in hosts:
            print hosts[host]['content']
    elif (options.del_ent):
        if options.dns is None:
            exit("Must specify a --dns argument")
        Cloudflare().delete_entry(options.dns)
    elif (options.append):
        Cloudflare().append_entry(options.dns, options.ip)
    elif options.services:
       for srv in Cloudflare().list_srv(options.dns):
        print srv
    elif (options.dns != None and options.ip != None):
        Cloudflare().create_entry(options.ip, options.dns)



if __name__ == "__main__":
    main()
