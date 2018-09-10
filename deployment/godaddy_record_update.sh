#! /bin/bash

set -eu

. /opt/godaddy/dns/locking

__prep_lock
exclusive_lock_now || exit 1

PROJECT_ENV=/opt/godaddy/env
PROJECT_LOC=PROJECT_ENV/lib/python3.6/site-packages/godaddy-dns

$PROJECT_ENV/bin/python $PROJECT_LOC/dns/godaddy_record_update.py %1 >> /var/log/yedor.net/godaddy_record_update.log

#source name_Env/bin/activate
## virtualenv is now active.
##
#/usr/bin/python3 godaddy-dns.py