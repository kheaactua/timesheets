#!/usr/bin/env python3

from __future__ import print_function
import sys, os
import json

# Import Yast Library modules
sys.path.append(os.path.abspath('yastlibs/python'))
from yast import *

try:
    with open('secret.json', 'r') as f: auth = json.load(f)
    print(auth)
except ValueError as e:
    print('Could not read login information out of secret.json file', file=sys.stderr)
    sys.exit(-1)

# Create instance of Yast class. All yast requests will
# be done through this object
yast = Yast()

# Log in to a Yast account to get an access hash.
hash = yast.login(auth.get('login'), auth.get('password'))

# Return value of library functions are False on error.
if hash == False:
    # Authentication failure. yast.getStatus() gives the
    # reason for the failure. Handle errors. Example:
    if yast.getStatus() == YastStatus.LOGIN_FAILURE:
        print('Wrong password or missing user')
    else:
        print('Other error')

records = yast.getRecords()
output = {'records': []}
for k,r in sorted(records.items()):
    output['records'].append({
        'startTime': r.variables['startTime'],
        'endTime':   r.variables['endTime'],
        'comment':   r.variables['comment'],
        'hours':     str(int(round((r.variables['endTime'] - r.variables['startTime'])/3600.0, 2))),
        'project':   r.project,
    })

print(json.dumps(output, indent=2, sort_keys=True))

# vim: ts=4 sts=4 sw=4 noet nowrap ffs=unix :
