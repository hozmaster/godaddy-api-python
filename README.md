# Godaddy DDNS Script

## Introduction
This script dynamically udpates GoDaddy DNS records. I have to use Godaddy for a domain and I wanted a way to update the dns record whenever the IP changed. This is particularly useful for home networks hosting websites where the domain is hosted at godaddy. This script uses the godaddy api. You can obtain information here as well as keys https://developer.godaddy.com/. Make sure you generate production keys, do not use the test key/secret.


## Dependencies
I build this with the python libraries already installed on the pfSense (FreeBSD) so I would not have to install any additional libraries in pfsense (Hence urllib2, i prefer requests)

- python3.6
- urllib5
- json

## Setup

Git clone project to /opt/godaddy-folder and after that the Normal python env setup procedures.

## Usage
godaddy_record_update.py -f [settings].json

Give name of settings json for application. Don't make changes directly to settings.json.example file, copy the example json file to another location path and rename to prefer name.

optionally you can run 'godaddy_record_update.py -h' for these same instructions.

## Cron It!
Obviously you do not want to have to run this script every time the IP changes. That's what cron is for. You can try it cmd line with crontab -e. Or you can go the easy way and install the Puppet or Ansible. Then schedule your cron job. Below is a sample cron job:

Normal way :

>2	\*	\*	\*	\*	root	/usr/local/bin/python3.6 [/path/to/]/godaddy_record_update.py /path/to/[settings].json


## Other

Since this application is bound by MIT license, you can use or fork this application pretty much freely. However, you
should delete any encrypted json files found this project from you copy of this repository.