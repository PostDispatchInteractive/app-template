#!/usr/bin/env python

"""
Commands for rendering various parts of the app stack.
"""

from glob import glob
import os

from fabric.api import local, task

# This is needed in render_all() to minify the HTML content
from htmlmin.main import minify

import app

def _fake_context(path):
    """
    Create a fact request context for a given path.
    """
    return app.app.test_request_context(path=path)

def _view_from_name(name):
    """
    Determine what module a view resides in, then get
    a reference to it.
    """
    bits = name.split('.')

    # Determine which module the view resides in
    if len(bits) > 1:
        module, name = bits
    else:
        module = 'app'

    return globals()[module].__dict__[name]

@task
def less():
    """
    Render LESS files to CSS.
    """
    for path in glob('less/*.less'):
        filename = os.path.split(path)[-1]
        name = os.path.splitext(filename)[0]
        out_path = 'www/css/%s.less.css' % name

        try:
            local('node_modules/less/bin/lessc %s %s' % (path, out_path))
        except:
            print('It looks like "lessc" isn\'t installed. Try running: "npm install"')
            raise

        # JOSH ADDITION: WRITE A MINIFIED VERSION
        with open(out_path, 'r') as less_css:
            min_path = 'www/css/%s.min.css' % name
            with open(min_path, 'w') as f:
                f.write( minify( less_css.read() ) )



@task(default=True)
def render_all( server_name=None, app_dir=None, project_slug=None ):
    """
    Render HTML templates and compile assets.
    """
    from flask import g

    less()

    # Using server name, app dir, and project slug to construct Flask's SERVER_NAME and APPLICATION_ROOT.
    # Setting these variables will ensure url_for() constructs correct URLs when deploying.
    if server_name and app_dir and project_slug:
        app.app.config['SERVER_NAME'] = server_name
        app.app.config['APPLICATION_ROOT'] = '/' + app_dir + '/' + project_slug

    compiled_includes = {}

    # Loop over all views in the app
    for rule in app.app.url_map.iter_rules():
        rule_string = rule.rule
        name = rule.endpoint

        # Skip utility views
        if name == 'static' or name.startswith('_'):
            print('Skipping %s' % name)
            continue

        # Skip routes with any() construction: 
        if 'any(' in rule_string:
            print('Skipping %s' % name)
            continue

        # Convert trailing slashes to index.html files
        if rule_string.endswith('/'):
            filename = 'www' + rule_string + 'index.html'
        elif rule_string.endswith('.html'):
            filename = 'www' + rule_string
        else:
            print('Skipping %s' % name)
            continue

        # Create the output path
        dirname = os.path.dirname(filename)

        if not (os.path.exists(dirname)):
            os.makedirs(dirname)

        print('Rendering %s' % (filename))

        # Render views, reusing compiled assets
        with _fake_context(rule_string):
            g.compile_includes = True
            g.compiled_includes = compiled_includes

            view = _view_from_name(name)

            content = view().data

            compiled_includes = g.compiled_includes

        # Minify HTML. Comment out the next three lines if you don't want to minify.
        content = unicode(content, 'utf-8')
        content = minify(content, remove_optional_attribute_quotes=False)
        content = content.encode('utf-8')

        # Write rendered view
        # NB: Flask response object has utf-8 encoded the data
        with open(filename, 'w') as f:
            f.write(content)

