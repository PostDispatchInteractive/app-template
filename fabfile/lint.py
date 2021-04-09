#!/usr/bin/env python

"""
Commands for linting JavaScript
"""

from glob import glob
import os

from fabric.api import local, task

import app


@task(default=True)
def lint():
    """
    Run ESLint on all .js files.
    """
    for path in glob('www/js/*.js'):
        filename = os.path.split(path)[-1]
        name = os.path.splitext(filename)[0]

        exceptions = ['app_config.js']
        if '.min.js' not in filename and filename not in exceptions:
            try:
                local( 'node_modules/eslint/bin/eslint.js %s || exit 0' % (path) )
            except:
                print('It looks like "eslint" isn\'t installed. Try running: "npm install"')
                raise

 