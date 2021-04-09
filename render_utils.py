#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This allows use of unicode characters in my comments below.

import codecs
from datetime import datetime
import json
import time
import urllib
import subprocess

from flask import Markup, g, render_template, request
from smartypants import smartypants

import app_config
import copytext

class BetterJSONEncoder(json.JSONEncoder):
    """
    A JSON encoder that intelligently handles datetimes.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        else:
            encoded_object = json.JSONEncoder.default(self, obj)

        return encoded_object

class Includer(object):
    """
    Base class for Javascript and CSS psuedo-template-tags.

    See `make_context` for an explanation of `asset_depth`.
    """
    def __init__(self, asset_depth=0):
        self.includes = []
        self.tag_string = None
        self.asset_depth = asset_depth

    def push(self, path):
        self.includes.append(path)

        return ''

    # --- BEGIN JOSH ADIITION ---
    def empty(self):
        del self.includes[:]

        return ''
    # --- END JOSH ADIITION ---

    def _compress(self):
        raise NotImplementedError()

    def _relativize_path(self, path):
        relative_path = path
        depth = len(request.path.split('/')) - (2 + self.asset_depth)

        while depth > 0:
            relative_path = '../%s' % relative_path
            depth -= 1

        return relative_path

    def render(self, path):
        if getattr(g, 'compile_includes', False):
            if path in g.compiled_includes:
                timestamp_path = g.compiled_includes[path]
            else:
                # Add a querystring to the rendered filename to prevent caching
                timestamp_path = '%s?%i' % (path, int(time.time()))

                out_path = 'www/%s' % path

                if path not in g.compiled_includes:
                    print('Rendering %s' % out_path)

                    with codecs.open(out_path, 'w', encoding='utf-8') as f:
                        f.write(self._compress())

                # See "fab render"
                g.compiled_includes[path] = timestamp_path

            markup = Markup(self.tag_string % self._relativize_path(timestamp_path))
        else:
            response = ','.join(self.includes)

            response = '\n'.join([
                self.tag_string % self._relativize_path(src) for src in self.includes
            ])

            markup = Markup(response)

        del self.includes[:]

        return markup

class JavascriptIncluder(Includer):
    """
    Psuedo-template tag that handles collecting Javascript and serving appropriate clean or compressed versions.
    """
    def __init__(self, *args, **kwargs):
        Includer.__init__(self, *args, **kwargs)

        self.tag_string = '<script type="text/javascript" src="%s"></script>'

    def _compress(self):
        output = []
        src_paths = []

        for src in self.includes:
            src_paths.append('www/%s' % src)
            print('- compressing %s' % src)

            # Switched from the Python jsmin module to Babel. It doesn't *truly* minify, but it allows me
            # to compile ES2015 javascript down to ES5 that IE and other older browsers will accept.
            try:
                compressed_src = subprocess.check_output(['node_modules/.bin/babel', 'www/'+src, '--minified'], encoding='UTF-8')
                output.append(compressed_src)
            except:
                print('It looks like "babel" isn\'t installed. Try running: "npm install"')
                raise

        context = make_context()
        context['paths'] = src_paths

        header = render_template('_js_header.js', **context)
        output.insert(0, header)

        return '\n'.join(output)

class CSSIncluder(Includer):
    """
    Psuedo-template tag that handles collecting CSS and serving appropriate clean or compressed versions.
    """
    def __init__(self, *args, **kwargs):
        Includer.__init__(self, *args, **kwargs)

        self.tag_string = '<link rel="stylesheet" type="text/css" href="%s" />'

    def _compress(self):
        output = []

        src_paths = []

        for src in self.includes:

            src_paths.append('%s' % src)

            try:
                compressed_src = subprocess.check_output(['node_modules/less/bin/lessc', '-x', src], encoding='UTF-8')
                output.append(compressed_src)
            except:
                print('It looks like "lessc" isn\'t installed. Try running: "npm install"')
                raise

        context = make_context()
        context['paths'] = src_paths

        header = render_template('_css_header.css', **context)
        output.insert(0, header)


        return '\n'.join(output)

def flatten_app_config():
    """
    Returns a copy of app_config containing only
    configuration variables.
    """
    config = {}

    # Only all-caps [constant] vars get included
    for k, v in app_config.__dict__.items():
        if k.upper() == k:
            config[k] = v

    return config

def make_context(asset_depth=0):
    """
    Create a base-context for rendering views.
    Includes app_config and JS/CSS includers.

    `asset_depth` indicates how far into the url hierarchy
    the assets are hosted. If 0, then they are at the root.
    If 1 then at /foo/, etc.
    """
    context = flatten_app_config()

    try:
        context['COPY'] = copytext.Copy(app_config.COPY_PATH)
    except copytext.CopyException:
        pass

    context['JS'] = JavascriptIncluder(asset_depth=asset_depth)
    context['CSS'] = CSSIncluder(asset_depth=asset_depth)

    return context

# --------------
# CUSTOM FILTERS
# --------------

def urlencode_filter(s):
    """
    Filter to urlencode strings.
    """
    if type(s) == 'Markup':
        s = s.unescape()

    # Evaulate COPY elements
    if type(s) is not str:
        s = str(s)

    s = s.encode('utf8')
    s = urllib.quote_plus(s)

    return Markup(s)

def smarty_filter(s):
    """
    Filter to smartypants strings.
    """
    if type(s) == 'Markup':
        s = s.unescape()

    # Evaulate COPY elements
    if type(s) is not str:
        s = str(s)

    s = s.encode('utf-8')
    s = smartypants(s)

    try:
        return Markup(s)
    except:
        print('This string failed to encode: %s' % s)
        return Markup(s)

def split_semicolon_filter(s):
    """
    Filter to take semicolon-delimited text and convert it to a list
    """
    if s is not None:
        return s.strip().split(';')
    return None

def convert_to_slug(s):
    """
    Very simple filter to slugify a string
    """
    if s is not None:
        return s.strip().lower().replace('.','').replace(' ','-').replace(',','-').replace('--','-')
    return None

def convert_to_int(s):
    """
    Filter to convert a string to an int    
    """
    if s is not None:
        return int( s.strip() )
    return None

def nat_sort(l,k=None,r=False):
    """
    Filter to apply natsort to a list 
    (This is a better way to sort for sorting strings with numbers)
    """
    from natsort import natsorted
    if l is not None:
        sl = []
        # Create a list of tuples for sorting
        for item in l:
            key = item[k]
            sl.append( (key, item) )
        # Use natsort to naturally sort the tuples by the key field
        sl = natsorted( sl, reverse=r )
        # Convert list of tuples back into normal list (basically throw out the key)
        sl = [ item[-1] for item in sl ]
        return sl
    return None

def cache_bust_filter(s):
    """
    Filter to append a cache-busting timestamp to a URL
    """
    if type(s) == 'Markup':
        s = s.unescape()

    # Evaulate COPY elements
    if type(s) is not str:
        s = str(s)

    timestamp = int(time.time())
    return Markup( s + str('?') + str(timestamp) )


# --------------
# CUSTOM TESTS
# --------------

def contains(value,check):
    if value is not None and check is not None:
        # First, encode them all as ASCII to remove problematic unicode characters (e.g. Jefferson County Library District 8¢ for the Library)
        # In Python3, this will convert them to bytes. So next, decode the bytes back to unicode text.
        check = check.encode('ascii','ignore').decode('UTF-8')
        value = value.encode('ascii','ignore').decode('UTF-8')
        if str(check) in str(value):
            return True
    return False
