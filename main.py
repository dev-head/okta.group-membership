#!/usr/bin/env python

import http.client
import json
import sys
import csv
import argparse
import os
import http 

def debug(output):
    print(json.dumps(output))


def debug_exit(output):
    debug(output)
    sys.exit()


def request(endpoint, api_version = 'v1'):
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "SSWS {}".format(api_key)
    }
    return makeRequest(domain, '/api/v1/{}'.format(endpoint), headers)


def makeRequest(domain, endpoint, headers):
    con         = http.client.HTTPSConnection(domain)
    con.set_debuglevel(0)
    con.request("GET", endpoint, None, headers)
    response    = con.getresponse()
    try:
        if 400 <= response.status < 600:
            raise NotImplementedError(response.status, response.reason, response.read())
        elif 500 <= response.status < 600:
            raise SystemError(response.status, response.reason, response.read())
        else:
            return json.loads(response.read())
    finally:
        con.close()

def getOrg():
    return request("/org")
    

def getGroups(limit=99999):
    return request("/groups?limit={}".format(limit))


def getUsers(limit=99999):
    return request("/users?limit={}".format(limit))


def getGroupMembership(group_id, limit=99999):
    return request("/groups/{}/users?limit={}".format(group_id, limit))


def getGroupMemberships():
    groups = getGroups()
    for group in groups:
        group['members']    = getGroupMembership(group['id'])
    return groups


def getUserGroupNames(user, groups):
    matches = []
    for group in groups:
        if 'members' in group:
            for member in group['members']:
                if member['id'] == user['id']:
                    matches.append(group['profile']['name'])

    return matches


def buildMembershipReport():
    groups  = getGroupMemberships()
    users   = getUsers()
    report  = []
    for user in users:
        user_groups = getUserGroupNames(user, groups)
        report.append({
            'firstName':    user['profile']['firstName'],
            'lastName':     user['profile']['lastName'],
            'email':        user['profile']['email'],
            'status':       user['status'],
            'created':      user['created'],
            'lastLogin':    user['lastLogin'],
            'lastUpdated':  user['lastUpdated'],
            'groups':       ', '.join(user_groups)
        })
    return report


def generateMembershipReport():
    data    = buildMembershipReport()
    writer  = csv.DictWriter(sys.stdout, fieldnames=data[0].keys(), quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for item in data:
        writer.writerow(item)


# @TODO allow output location to be passed so we can make the interaction with the user more friendly.
def main():
    """
    Main entry into the scripting here, basically allowing for you to pass
    in your domain and api-key; which is either
    ./main.py --domain hello --api-key blahblah
    or use environment vars (OKTA_DOMAIN_NAME, OKTA_API_TOKEN)
    if none are provided, the script will ask you to provide them.
    """
    global domain   # global because i'm too lazy to get classy.
    global api_key

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain')
    parser.add_argument('-a', '--api-key')

    args        = parser.parse_args()
    domain      = os.getenv('OKTA_DOMAIN_NAME')
    api_key     = os.getenv('OKTA_API_TOKEN')

    # override the env vars if options passed in.
    domain      = args.domain if args.domain else domain
    api_key     = args.api_key if args.api_key else api_key

    if not domain:
        domain  = raw_input("What is your domain name [example.okta.com]? ")

    if not api_key:
        api_key = raw_input("What is your API Token? ")


    generateMembershipReport()


main()
