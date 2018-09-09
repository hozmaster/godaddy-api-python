#! /bin/bash
# 0,30 * * * * cd /root/environments && /usr/bin/python3 script.py > /tmp/tw$

source name_Env/bin/activate

# virtualenv is now active.
#
/usr/bin/python3 go_daddy-dns.py