from subprocess import call
import re
import sys
import http.client
import urllib.request
import json


class GoDaddyDNSUpdater(object):

    def __init__(self, file: str):
        self.settings = json.load(open(file))
        self.api_key = ""
        self.secret = ""

    def restart_haproxy(self):

        call(["/usr/local/etc/rc.d/haproxy.sh", "restart"])

    def get_domain_info(self, domain):

        url = "api.ote-godaddy.com"
        path = "/v1/domains/available?domain={}".format(domain)
        connection = http.client.HTTPSConnection(url)

        headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
                   'Accept': 'application/json'}

        connection.request("GET", path, "", headers)
        response = connection.getresponse()
        print("Status: {} and reason: {}".format(response.status, response.reason))
        print(response.read().decode())

        connection.close()

        pass

    def get_domain_ip(self, domain):
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
            for hostname in domain['a-records']:
                self.get_domain_info(domain['domain'])

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