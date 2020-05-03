from subprocess import call
import re
import sys
import http.client
import socket
import fcntl
import struct
import datetime
import ipaddress
import urllib.request
import json
import argparse

api_test_base_url = "api.ote-godaddy.com"
api_base_url = "api.godaddy.com"


class GoDaddyDNSRecordUpdate(object):

    def __init__(self, settings_file: str, mode, noop):
        self.settings = json.load(open(settings_file))
        self.go_daddy_url = api_base_url

        test = 'test' in self.settings

        if test is True:
            self.go_daddy_url = api_test_base_url

        self.api_key = ""
        self.secret = ""
        self.mode = mode
        self.noop = noop
        self.response_code = 200

    def time_stamp(self):

        st = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return st

    def make_https_put_req(self, path: str, resource: str, headers: dict):
        connection = http.client.HTTPSConnection(api_base_url)
        connection.request("PUT", path, resource, headers)

        response = connection.getresponse()
        self.response_code = response.code

        response_data = response.read().decode()

        if len(response_data):
            data = json.loads()
        else:
            data = ""
        connection.close()
        return data

    def get_primary_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()

        return ip

    def get_public_ip_via_http(self):

        """get Public IP of network."""
        req = urllib.request.Request(self.settings['config']["ip.resolver"])
        response = urllib.request.urlopen(req)
        pub_ip = str(response.read())
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', pub_ip)

        return ip[0]

    def get_json_from_response(self, response: object):

        data = response.read().decode()
        response_dict = json.loads(data)

        return response_dict

    def make_https_get_req(self, path: str, resource: str, headers: dict):
        connection = http.client.HTTPSConnection(self.go_daddy_url)
        connection.request("GET", path, resource, headers)

        response = connection.getresponse()

        self.response_code = response.code

        data = json.loads(response.read().decode())

        connection.close()
        return data

    def get_domain_available_info(self, domain):

        path = "/v1/domains/available?domain={}".format(domain)

        headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
                   'Accept': 'application/json'}

        return self.make_https_get_req(path, "", headers)

    def get_domains_records(self, domain, type: str, name):
        path = "/v1/domains/{}/records/{}/{}".format(domain, type, name)

        headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
                   'Accept': 'application/json'}

        json_data = self.make_https_get_req(path, "", headers)

        return json_data

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        buffer = fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s',
                        bytes(ifname[:15], 'utf-8'))
        )[20:24]

        return socket.inet_ntoa(buffer)

    def put_domain_update_record(self, domain: str, data: str, type: str, name: str) -> object:
        """Update Godaddy  record."""
        req_content = json.dumps([{"data": data,
                                   "ttl": 3600,
                                   "name": name,
                                   "type": type
                                   }])

        path = "https://api.godaddy.com/v1/domains/{}/records/{}/{}".format(domain, type, name)
        headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'
                   }

        return self.make_https_put_req(path, req_content, headers)

    def write_output(self, output):

        time_stamp = self.time_stamp()

        print('{} {}'.format(time_stamp, output))

    def main(self):

        go_daddy = self.settings["godaddy"]

        self.api_key = go_daddy['api.key']
        self.secret = go_daddy['api.secret']

        cur_ip_output = "public ip : {}"

        if self.mode == 'http':
            pub_ip = self.get_public_ip_via_http()
        elif self.mode == 'iface':
            iface = self.settings['config']['iface']
            pub_ip = self.get_ip_address(iface)
        else:
            # this is most uncertain way to catch current ip since it may change during statups
            pub_ip = self.get_primary_ip()

        self.write_output(cur_ip_output.format(pub_ip))
        if ipaddress.ip_address(pub_ip).is_private is True:
            print("Private ip address detected. Cannot continue since it's not valid ip for public address ")
            return 1

        for domain in go_daddy['domains']:
            # response = self.get_domain_available_info(domain['domain'])
            records = domain['records']
            for record in records:
                live_info = self.get_domains_records(domain['domain'], record['type'], record['name'])
                output = "godaddy: domain {}, type: {}"
                self.write_output(output.format(domain['domain'], record['type']))
                if self.response_code == 200:
                    record_ip = ""
                    if len(live_info):
                        record_ip = live_info[0]['data']
                    if record_ip != pub_ip:
                        if not self.noop:
                            self.write_output("... Current pub_ip do not match with dns records ! Update it.")
                            self.put_domain_update_record(domain['domain'], pub_ip, record['type'], record['name'])
                            if self.response_code is 200:
                                self.write_output("Record updated or created.")
                            else:
                                self.write_output("Ip update req failed")
                        else:
                            self.write_output("... noop set, do not update records.")

                    else:
                        self.write_output("... ip addresses match, no update needed.")
                else:
                    output = " got invalid response from the godaddy service: {}"
                    self.write_output(output.format(self.response_code))
                    message = live_info['message']
                    code = live_info['code']
                    output2 = " godaddy: code : {}, message : {} "
                    self.write_output(output2.format(code, message))
        return 0


def check_arg(args):
    parser = argparse.ArgumentParser(description='Script to update GoDaddy DNS records.')
    parser.add_argument('-f', '--file',
                        help='Settings file. Must be json format.',
                        default='', required=True),
    parser.add_argument('-m', '--mode',
                        help='Get IP address using ip route or using http fetch',
                        choices=['http', 'route', 'iface'],
                        default='route', required=False),
    parser.add_argument('-n', '--noop',
                        help='When set, script is not send update request to the provider',
                        action='store_true', required=False),

    results = parser.parse_args(args)
    return results


# you can run this function from command line and this will catch it
if __name__ == "__main__":

    args = check_arg(sys.argv[1:])
    ret_code = 0
    if args.file is not '':
        ret_code = GoDaddyDNSRecordUpdate(args.file, args.mode, args.noop).main()
    else:
        ret_code = 1

    exit(ret_code)
