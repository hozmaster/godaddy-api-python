from subprocess import call
import re
import sys
import http.client
import urllib.request
import json

# api_base_url = "api.ote-godaddy.com"
api_base_url = "api.godaddy.com"


class GoDaddyDNSUpdater(object):

    def __init__(self, file: str):
        self.settings = json.load(open(file))
        self.api_key = ""
        self.secret = ""

    def restart_haproxy(self):

        call(["/usr/local/etc/rc.d/haproxy.sh", "restart"])

    def make_https_get_req (self, path: str, resource: str, headers: dict):

        connection = http.client.HTTPSConnection(api_base_url)
        connection.request("GET", path, resource, headers)

        response = connection.getresponse()
        data = response.read().decode()
        response_dict = json.loads(data)

        connection.close()

        return response_dict

    def get_domain_available_info(self, domain):

        path = "/v1/domains/available?domain={}".format(domain)

        headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
                   'Accept': 'application/json'}

        return self.make_https_get_req(path, "", headers)

    def get_domains_records (self, domain, type, name):
        path = "/v1/domains/{}/records/{}/{}".format(domain, type, name)

        headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
                   'Accept': 'application/json'}

        return self.make_https_get_req(path, "", headers)

    def get_domain_ip_record(self, domain):
        pass

    # def get_domain_ip_goddy(self, domain, hostname):
    #
    #     """get IP of A record from godaddy."""
    #     url = "https://api.ote-godaddy.com/v1/domain/{}".format(domain)
    #     headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
    #                'Accept': 'application/json'}
    #
    #     request = urllib.request.Request(url, headers=headers)
    #
    #     # response = urllib.request.urlopen(request)
    #     response = urllib.request.urlopen(request).read()
    #
    #     #
    #     if response.getcode() == 200:
    #         json_data = json.load(response)
    #     #     name = json_data[0]['name']
    #     #     godaddyIP = json_data[0]['data']
    #     #     if name == hostname:
    #     #         return godaddyIP
    #     #     else:
    #     #         print('godaddy hostname: {} does not match searched hostname: {}'.format(name, hostname))
    #     else:
    #          print(response.getcode())
    #          print(response.read())
    #     pass

    def get_public_ip(self):

        """get Public IP of network."""
        req = urllib.request.Request(self.settings["ip.resolver"])
        response = urllib.request.urlopen(req)
        pub_ip = str(response.read())

        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', pub_ip)
        return ip[0]

    def main(self):

        public_ip = self.get_public_ip ()

        godaddy = self.settings["godaddy"]

        self.api_key = godaddy['api.key']
        self.secret = godaddy['api.secret']

        for domain in godaddy['domains']:
            domain_info = self.get_domain_available_info(domain['domain'])
            print(domain_info)
            records = domain['records']
            for record in records:
                record_info = self.get_domains_records(domain['domain'], record['type'], record['name'])
                print(record_info)

        print(public_ip)


# you can run this function from command line and this will catch it
if __name__ == "__main__":

    args = sys.argv
    settings_file = ""

    if len(args) == 2:

        settings_file = args[1]

    else:
        print('Try again with correct parameters!')
        sys.exit(1)

    GoDaddyDNSUpdater(settings_file).main()
