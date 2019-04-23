#!/usr/bin/env python3

from __future__ import print_function
import sys, os
import json
import csv
import argparse
from time import gmtime

# Import Yast Library modules
sys.path.append(os.path.abspath('yastlibs/python'))
from yast import *

flat_project_delimeter = '.'

def load_data():
    try:
        with open('secret.json', 'r') as f: auth = json.load(f)
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
    output = {'records': [], 'projects': [], 'flatProjects': [], 'folders': []}
    for k,r in sorted(records.items()):
        output['records'].append({
            'startTime': r.variables['startTime'],
            'endTime':   r.variables['endTime'],
            'comment':   r.variables['comment'],
            'hours':     str(int(round((r.variables['endTime'] - r.variables['startTime'])/3600.0, 2))),
            'project':   r.project,
        })

    for id,f in yast.getFolders().items():
        output['folders'].append({
            'name': f.name,
            'id': id,
            'parentId': f.parentId
        })

    def find_folder(id):
        for f in output['folders']:
            if f['id'] == id:
                return f

    projects = yast.getProjects()
    for id,p in projects.items():
        output['projects'].append({
            'name':     p.name,
            'id':       id,
            'parentId': p.parentId
        })

    output['flatProjects'] = output['projects']
    for p in output['flatProjects']:
        if p['parentId'] in (-1, 0):
            print('Error, no parent')
        else:
            parent_folder = find_folder(p['parentId'])
            if parent_folder['parentId'] not in (0, -1):
                p['name'] = flat_project_delimeter.join([parent_folder['name'], p['name']])
                p['parentId'] = parent_folder['parentId']


    return output, auth

def export_json(data):
    with open('yast.json', 'w') as outp:
        json.dump(data, outp, indent=2, sort_keys=True)

def export_toggl(data, auth):
    """ Export in CSV described in https://support.toggl.com/import-and-export/csv-import/editing-and-uploading-a-csv-file """

    headers = [
        [
            'User',        # Req
            'Email',
            'Client',
            'Project',
            'Task',        # Req
            'Description', # Req
            'Billable',    # Req
            'Start date',  # YYYY-MM-DD
            'Start time',  # HH:MM:SS
            'Duration',    # HH:MM:SS
            # 'Tags',
        ]
    ]

    def find_item(id, items):
        for f in items:
            if f['id'] == id:
                return f

    with open('yast.csv', 'w') as outp:
        writer = csv.writer(outp, headers)
        writer.writerows(headers)

        for r in data['records']:
            project = find_item(r['project'], data['flatProjects'])
            client  = find_item(project['parentId'], data['folders'])

            start_ts = datetime.datetime.fromtimestamp(r['startTime'])
            startDate_str = start_ts.strftime('%Y-%m-%d')
            startTime_str = start_ts.strftime('%H:%M:%S')

            duration = r['endTime'] - r['startTime']
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

            writer.writerow([
                auth['name'],     # User
                auth['email'],    # Email
                client['name'],   # Client
                project['name'],  # Project
                '',               # Task
                r['comment'],     # Description
                'No',             # Billable
                startDate_str,    # Start date
                startTime_str,    # Start time
                duration_str,     # Duration
            ])

        outp.close()

def main():
    parser = argparse.ArgumentParser(
        description='Simple exporter for Yast records'
    )

    parser.add_argument('--json',
        action='store_true',
        dest='json',
        required=False,
        help='Export data into a JSON format'
    )

    parser.add_argument('--toggl',
        action='store_true',
        dest='toggl',
        required=False,
        help='Export data into a format importable by toggl'
    )

    try:
        args = parser.parse_args()
    except ValueError as e:
        print('Invalid options.', e, file=sys.stderr)
        sys.exit(1)

    data, auth = load_data()
    if args.json:
        export_json(data)
    if args.toggl:
        export_toggl(data, auth)


if __name__ == '__main__':
    main()

# vim: ts=4 sts=4 sw=4 noet nowrap ffs=unix :
