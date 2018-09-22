#! /bin/bash

set -eu

PROJECT_LOC=/opt/godaddy-api-python
PYTHON_ENV=/usr/bin/python3

/usr/bin/python3 $PROJECT_LOC/dns/godaddy_record_update.py -f $1 >> /var/log/yedor.net/godaddy_record_update.log
