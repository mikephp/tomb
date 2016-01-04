'''
    This script will attempt to open your webbrowser,
    perform OAuth 2 authentication and print your access token.

    It depends on two libraries: oauth2client and gflags.

    To install dependencies from PyPI:

    $ pip install python-gflags oauth2client

    Then run this script:

    $ python get_oauth2_token.py

    This is a combination of snippets from:
    https://developers.google.com/api-client-library/python/guide/aaa_oauth
'''

from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from oauth2client.tools import run_flow
from oauth2client.file import Storage
import argparse

CLIENT_ID = '962722732387-okdgpbfgsn283j59r4sc0ea9q782j2ir.apps.googleusercontent.com'
CLIENT_SECRET = 'HuqUlDJiWN89SJLDa1Xlbcj1'

parser = argparse.ArgumentParser(parents=[tools.argparser])
flags = parser.parse_args()
print(flags)

flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
                           redirect_uri='http://localhost:8082/auth_return')

storage = Storage('creds.data')

credentials = run_flow(flow, storage, flags)

print "access_token: %s" % credentials.access_token
