# okta.group-membership

Okta Group Membership Report
============================

Use Okta API to generate report of each user with their assigned groups. This exists due to Okta having no support to find out what users are in which groups and provides these as csv output for building reports.


#### Generate User Group Assignments 
```
./main.py --domain example.okta.com --api-key $APIKEY$ > group-memberships.$(date +%m-%d-%Y).csv
```
