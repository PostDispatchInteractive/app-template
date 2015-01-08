#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

from fabric.api import task
from termcolor import colored

import app_config
from etc.gdocs import GoogleDoc

import re

@task(default=True)
def update():
    """
    Downloads a Google Doc as an Excel file.
    """
    if app_config.COPY_GOOGLE_DOC_URL == None:
        print colored('You have set COPY_GOOGLE_DOC_URL to None. If you want to use a Google Sheet, set COPY_GOOGLE_DOC_URL to the URL of your sheet in app_config.py', 'blue')
        return
    else:
        doc = {}
        url = app_config.COPY_GOOGLE_DOC_URL

        # Search for oldstyle spreadsheets URL in this form: https://docs.google.com/spreadsheet/ccc?key=0Ah9eiJcTTiAKdDFxQnA4X3B0Z09ZUGRYWHhmUmZDblE&usp=drive_web#gid=1
        search1 = re.search(r'ccc\?key=(.{44})', url)
        # Search for newstyle spreadsheets URL in this form: https://docs.google.com/spreadsheets/d/1A1aXUqMyXqQ9hcdLAE1WqBTkBLTAKA6ze4Ei-FQwlQ0/edit#gid=283902313
        search2 = re.search(r'spreadsheets/d/(.{44})', url)
        # Search for key only, without URL junk. This one is more of a hail-mary.
        search3 = re.search(r'^(\S{44})$', url)
        if search1:
            doc['key'] = search1.group(1)
        elif search2:
            doc['key'] = search2.group(1)
        elif search3:
            doc['key'] = search3.group(1)
        else:
            print colored('Failed to parse your Google docs URL. Please check that COPY_GOOGLE_DOC_URL is set properly in app_config.py', 'blue')
            return

        g = GoogleDoc(**doc)
        g.get_auth()
        g.get_document()

