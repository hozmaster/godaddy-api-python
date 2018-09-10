from subprocess import call
import re
import sys
import http.client
import urllib.request
import json

#test url,
api_base_url = "api.ote-godaddy.com"

#production url
#api_base_url = "api.godaddy.com"


class GoDaddyDNSUpdater(object):

    def __init__(self, file: str):
        self.settings = json.load(open(file))
        self.api_key = ""
        self.secret = ""
        self.response_code = 200

    def restart_haproxy(self):

        call(["/usr/local/etc/rc.d/haproxy.sh", "restart"])

    def make_https_put_req(self, path: str, resource: str, headers: dict):
        connection = http.client.HTTPSConnection(api_base_url)
        connection.request("PUT", path, resource, headers)

        response = connection.getresponse()
        self.response_code = response.code
        data = json.loads(response.read().decode())

        connection.close()

        return data

    def get_json_from_response (self, response: object):

        data = response.read().decode()
        response_dict = json.loads(data)

        return response_dict

    def make_https_get_req(self, path: str, resource: str, headers: dict):
        connection = http.client.HTTPSConnection(api_base_url)
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

    def get_domain_ip_record(self, domain):
        pass

    def show_failed_json (self, code, error_json):
        output = " got invalid response from godaddy: {}"
        print(output.format(code))
        message = error_json['message']
        code = error_json['code']
        output2 = " godaddy: code : {}, message : {} "
        print(output2.format(code, message))

    def put_domain_update_record(self, domain: str, ip_address: str, type: str, name: str) -> str:
        """Update Godaddy  record."""
        data = json.dumps([{"data": ip_address,
                            "ttl": 3600,
                            "name": name,
                            "type": type
                            }])

        path = "https://api.godaddy.com/v1/domains/{}/records/{}/{}".format(domain, type, name)
        headers = {'Authorization': 'sso-key {}:{}'.format(self.api_key, self.secret),
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'
                   }

        return self.put_domain_update_record(path, data, headers)

    def get_public_ip(self):

        """get Public IP of network."""
        req = urllib.request.Request(self.settings["ip.resolver"])
        response = urllib.request.urlopen(req)
        pub_ip = str(response.read())

        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', pub_ip)
        return ip[0]

    def main(self):

        public_ip = self.get_public_ip()
        print(public_ip)

        godaddy = self.settings["godaddy"]

        self.api_key = godaddy['api.key']
        self.secret = godaddy['api.secret']

        for domain in godaddy['domains']:
            # response = self.get_domain_available_info(domain['domain'])
            records = domain['records']
            for record in records:
                record_info = self.get_domains_records(domain['domain'], record['type'], record['name'])
                output = "godaddy: domain {}, type: {}"
                print (output.format(domain['domain'], record['type']))
                if self.response_code == 200:

                    name = record_info[0]['name']
                    current_ip = record_info[0]['data']
                    record_type = record_info[0]['type']

                    if current_ip != public_ip:
                        print("... Current ip do not match ! update it.")
                        update_ip_info = self.put_domain_update_record(domain['domain'], public_ip, record_type, name )
                        print(update_ip_info)
                    else:
                        print("... ip addresses match, skip it.")
                else:
                    self.show_failed_json (self.response_code, record_info)


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
