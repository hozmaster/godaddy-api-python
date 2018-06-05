import os
import re
import sys
import urllib.request
import json


class GoDaddyDNSUpdater(object):

    def __init__(self, settings_file: str):

        self.settings_json = settings_file
        self.settings = json.load(open(self.settings_json))
        pass

    def get_public_ip(self):

        """get Public IP of network."""
        req = urllib.request.Request(self.settings["ip.resolver"])
        response = urllib.request.urlopen(req)
        pub_ip = str(response.read())

        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', pub_ip )
        return ip[0]

    def main(self):

        public_ip = self.get_public_ip ()
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
