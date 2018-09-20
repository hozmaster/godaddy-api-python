from subprocess import call
import re
import sys
import http.client
import urllib.request
import json
import argparse

api_base_url = "api.ote-godaddy.com"
# api_base_url = "api.godaddy.com"


class GoDaddyDNSRecordUpdate(object):

    def __init__(self, file: str):
        self.settings = json.load(open(file))
        self.api_key = ""
        self.secret = ""
        self.response_code = 200

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

    def main(self):

        go_daddy = self.settings["godaddy"]

        self.api_key = go_daddy['api.key']
        self.secret = go_daddy['api.secret']

        for domain in go_daddy['domains']:
            # response = self.get_domain_available_info(domain['domain'])
            records = domain['records']
            for record in records:
                live_info = self.get_domains_records(domain['domain'], record['type'], record['name'])
                output = "godaddy: domain {}, type: {}"
                print (output.format(domain['domain'], record['type']))
                if self.response_code == 200:
                    current_data = ""
                    if len(live_info):
                        current_data = live_info[0]['data']
                    if current_data != record['data']:
                        print("... Current data do not match ! update it.")
                        self.put_domain_update_record(domain['domain'], record['data'], record['type'], record['name'])
                        if self.response_code is 200:
                            print("Update or creation record was done ")
                        else:
                            print("Operation failed")

                    else:
                        print("... data info addresses match, skip it.")
                else:
                    output = " got invalid response from godaddy: {}"
                    print(output.format(self.response_code))
                    message = live_info['message']
                    code = live_info['code']
                    output2 = " godaddy: code : {}, message : {} "
                    print(output2.format(code, message))


def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Script to update GoDaddy DNS records.')
    parser.add_argument('-f', '--file',
                        help='settings file. Must be json format.',
                        default='', required=True)

    results = parser.parse_args(args)
    return results.file


# you can run this function from command line and this will catch it
if __name__ == "__main__":

    file = check_arg(sys.argv[1:])

    if file is not '':
        GoDaddyDNSRecordUpdate(file).main()
