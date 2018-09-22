#! /bin/bash

set -eu

PROJECT_LOC=/opt/godaddy-api-python
PYTHON_ENV=/usr/bin/python3

# . $PROJECT_LOC/locking

#__prep_lock
#exclusive_lock_now || exit 1

/usr/bin/python3 $PROJECT_LOC/dns/godaddy_record_update.py -f $1 >> /var/log/yedor.net/godaddy_record_update.log

#source name_Env/bin/activate
## virtualenv is now active.
##
#/usr/bin/python3 godaddy-dns.py
