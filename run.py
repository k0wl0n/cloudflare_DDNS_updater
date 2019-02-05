#!/usr/bin/env python


import sys
import argparse
import requests


def get_public_ip():
    return requests.get('http://ip.42.pl/raw').content


class CloudFlareDNS(object):
    API_URI = "https://api.cloudflare.com/client/v4/"
    DNS_ENDPOINT = "zones/%(zone_id)s/dns_records"

    def __init__(self, api_key, zone_id, email):
        self.api_key = api_key
        self.zone_id = zone_id
        self.email = email
        self.dns_uri = self.API_URI + (
            self.DNS_ENDPOINT % {'zone_id': zone_id})
        self.headers = {"X-Auth-Email": email, "X-Auth-Key": api_key,
                        "Content-Type": "application/json"}

    def get_domain_by_name(self, domain_name):
        domains = requests.get(
            self.dns_uri, headers=self.headers).json()["result"]

        domain_result = None
        for domain in domains:
            if domain["name"] == domain_name:
                domain_result = domain
        if not domain_result:
            raise ValueError("Domain name %s does not exist" % domain_name)

        return domain_result

    def update_dns(self, domain_name):
        domain = self.get_domain_by_name(domain_name)
        curr_pub_ip = get_public_ip()
        print(get_public_ip())

        if domain["content"] != curr_pub_ip:
            payload = {"type": domain["type"], "name": domain_name,
                       "content": curr_pub_ip, "proxied": domain["proxied"]}
            endpoint = "%s/%s" % (self.dns_uri, domain["id"])
            r = requests.put(endpoint, headers=self.headers, json=payload)
            r.raise_for_status()


def error(msg):
    print >> sys.stderr, msg
    sys.exit(1)


def main():
    API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    ZONE_ID = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    EMAIL_ID = "wahyuanggana@email.com"
    DNS_TO_UPDATE = "dynamic.example.com"

    try:
        client = CloudFlareDNS(API_KEY,ZONE_ID,EMAIL_ID)
        client.update_dns(DNS_TO_UPDATE)
    except ValueError as ex:
        error(ex.message)
    print("Success")


if __name__ == "__main__":
    main()
