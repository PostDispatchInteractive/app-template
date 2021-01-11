#!/usr/bin/env python
"""
Example application views.

Note that `render_template` is wrapped with `make_response` in all application
routes. While not necessary for most Flask apps, it is required in the
App Template for static publishing.
"""

import app_config
import json
import oauth
import static

from flask import Flask, make_response, render_template
from render_utils import make_context, smarty_filter, urlencode_filter
from werkzeug.debug import DebuggedApplication

# This is needed by the response_minify() function below
from htmlmin.main import minify

# This is needed by the less() function below
from fabric.api import local

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')

@app.route('/')
@oauth.oauth_required
def index():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    context = make_context()
    context['directory_depth'] = 0

    with open('data/featured.json') as f:
        context['featured'] = json.load(f)

    return make_response(render_template('index.html', **context))

@app.route('/404.html')
def four_oh_four():
    context = make_context()
    context['directory_depth'] = 0

    return make_response(render_template('404.html', **context))

@app.errorhandler(404)
def page_not_found(e):
    context = make_context()

    return make_response(render_template('404.html', **context))


@app.route('/css/<path:path>')
def less(path):
    """
    Render LESS files to CSS.
    """
    file_prefix = path.split('.')[0]
    srcfile = 'less/%s.less' % file_prefix
    outfile = 'www/css/%s.min.css' % file_prefix
    name = '%s.min.css' % file_prefix
    try:
        # run the LESS compiler, with --clean-css option set to minify, to generate static .css file
        local('node_modules/less/bin/lessc --clean-css %s %s' % (srcfile, outfile))
        # use Flask's send_from_directory to serve the static .css file
        return send_from_directory('www/css', name)
    except Exception as e:
        print('It looks like "lessc" isn\'t installed. Try running: "npm install"')
        print(e)

@app.after_request
def response_minify(response):
    """
    Minify html response to decrease site traffic
    """
    if response.content_type == 'text/html; charset=utf-8':
        response.set_data(
            minify(response.get_data(as_text=True))
        )

        return response
    return response


app.register_blueprint(static.static)
app.register_blueprint(oauth.oauth)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app

# Catch attempts to run the app directly
if __name__ == '__main__':
    print('This command has been removed! Please run "fab app" instead!')
