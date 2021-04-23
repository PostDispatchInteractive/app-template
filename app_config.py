#!/usr/bin/env python

"""
Project-wide application configuration.

DO NOT STORE SECRETS, PASSWORDS, ETC. IN THIS FILE.
They will be exposed to users. Use environment variables instead.
See get_secrets() below for a fast way to access them.
"""

import os

from authomatic.providers import oauth2
from authomatic import Authomatic


"""
NAMES
"""
# Project name to be used in urls
# Use dashes, not underscores!
PROJECT_SLUG = '$NEW_PROJECT_SLUG'

# Project name to be used in file paths
PROJECT_FILENAME = '$NEW_PROJECT_SLUG'

# The name of the repository containing the source
REPOSITORY_NAME = '$NEW_PROJECT_SLUG'
GITHUB_USERNAME = 'PostDispatchInteractive'
REPOSITORY_URL = 'git@github.com:%s/%s.git' % (GITHUB_USERNAME, REPOSITORY_NAME)
REPOSITORY_ALT_URL = None # 'git@bitbucket.org:nprapps/%s.git' % REPOSITORY_NAME'

# Setting this to true will force the development server (localhost) to run in SSL mode.
# SSL mode requires the existence of a self-signed certificate from the /ssl-certificate/ repo.
# The repo can be found here: https://github.com/PostDispatchInteractive/ssl-certificate
USE_SSL_DEV = True
if USE_SSL_DEV:
    # Keep track of the directory where this script is running
    app_path = os.path.dirname(os.path.realpath(__file__))
    projects_path = os.path.dirname(app_path)
    SSL_CERT = os.path.join(projects_path, 'ssl-certificate/certificate/localhost.crt')
    SSL_KEY = os.path.join(projects_path, 'ssl-certificate/certificate/server.key')

# Project name used for assets rig
# Should stay the same, even if PROJECT_SLUG changes
ASSETS_SLUG = '$NEW_PROJECT_SLUG'

"""
DEPLOYMENT
"""
PRODUCTION_S3_BUCKET = {
    'bucket_name': 'graphics.stltoday.com',
    'server_domain': 'graphics.stltoday.com',
    'server_dir': 'graphics.stltoday.com',
    'app_dir': 'apps'
}

STAGING_S3_BUCKET = {
    'bucket_name': 'staging-graphics.stltoday.com',
    'server_domain': 'graphics.stltoday.com',
    'server_dir': 'staging-graphics.stltoday.com',
    'app_dir': 'apps'
}

ASSETS_S3_BUCKET = {
    'bucket_name': 'graphics.stltoday.com',
    'server_domain': 'graphics.stltoday.com',
    'server_dir': 'graphics.stltoday.com',
    'app_dir': 'apps'
}

S3_USER = 'newsroom'

DEFAULT_MAX_AGE = 20 
ASSETS_MAX_AGE = 86400

PRODUCTION_SERVERS = ['graphics.stltoday.com']
STAGING_SERVERS = ['staging-graphics.stltoday.com']

# Should code be deployed to the web/cron servers?
DEPLOY_TO_SERVERS = False

SERVER_USER = 'newsroom'
SERVER_PYTHON = 'python2.7'
SERVER_PROJECT_PATH = '/home/%s/apps/%s' % (SERVER_USER, PROJECT_FILENAME)
SERVER_REPOSITORY_PATH = '%s/repository' % SERVER_PROJECT_PATH
SERVER_VIRTUALENV_PATH = '%s/virtualenv' % SERVER_PROJECT_PATH

# Should the crontab file be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_CRONTAB = False

# Should the service configurations be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_SERVICES = False

UWSGI_SOCKET_PATH = '/tmp/%s.uwsgi.sock' % PROJECT_FILENAME

# Services are the server-side services we want to enable and configure.
# A three-tuple following this format:
# (service name, service deployment path, service config file extension)
SERVER_SERVICES = [
    ('app', SERVER_REPOSITORY_PATH, 'ini'),
    ('uwsgi', '/etc/init', 'conf'),
    ('nginx', '/etc/nginx/locations-enabled', 'conf'),
]

# These variables will be set at runtime. See configure_targets() below
S3_BUCKET = None
S3_BASE_URL = None
S3_DEPLOY_URL = None
SERVERS = []
SERVER_BASE_URL = None
SERVER_LOG_PATH = None
DEBUG = True

"""
COPY EDITING
"""
COPY_GOOGLE_DOC_KEY = '1e-LKA5kIqumSbl79sNd9NDPFcLDxlZdzAfZ_UTHQWFM'
COPY_PATH = 'data/copy.xlsx'

"""
SHARING
"""
SHARE_URL = 'https://%s/%s/' % (PRODUCTION_S3_BUCKET['bucket_name'], PROJECT_SLUG)


"""
OAUTH
"""

GOOGLE_OAUTH_CREDENTIALS_PATH = '~/.google_oauth_credentials'

authomatic_config = {
    'google': {
        'id': 1,
        'class_': oauth2.Google,
        'consumer_key': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
        'consumer_secret': os.environ.get('GOOGLE_OAUTH_CONSUMER_SECRET'),
        'scope': ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email'],
        'offline': True,
    },
}

authomatic = Authomatic(authomatic_config, os.environ.get('AUTHOMATIC_SALT'))

"""
Utilities
"""
def get_secrets():
    """
    A method for accessing our secrets.
    """
    secrets_dict = {}

    for k,v in os.environ.items():
        if k.startswith(PROJECT_SLUG):
            k = k[len(PROJECT_SLUG) + 1:]
            secrets_dict[k] = v

    return secrets_dict

def configure_targets(deployment_target):
    """
    Configure deployment targets. Abstracted so this can be
    overriden for rendering before deployment.
    """
    global S3_BUCKET
    global S3_BASE_URL
    global S3_DEPLOY_URL
    global SERVERS
    global SERVER_BASE_URL
    global SERVER_LOG_PATH
    global DEBUG
    global DEPLOYMENT_TARGET
    global ASSETS_MAX_AGE

    if deployment_target == 'production':
        S3_BUCKET = PRODUCTION_S3_BUCKET
        S3_BASE_URL = '/home/%s/%s/public_html/%s/%s' % (S3_USER, S3_BUCKET['bucket_name'], S3_BUCKET['app_dir'], PROJECT_SLUG)
        S3_DEPLOY_URL = '%s@%s:/home/%s/%s/public_html/%s/%s' % (S3_USER, S3_BUCKET['server_domain'], S3_USER, S3_BUCKET['bucket_name'], S3_BUCKET['app_dir'], PROJECT_SLUG)
        SERVERS = PRODUCTION_SERVERS
        SERVER_BASE_URL = 'https://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DEBUG = False
        ASSETS_MAX_AGE = 86400
    elif deployment_target == 'staging':
        S3_BUCKET = STAGING_S3_BUCKET
        S3_BASE_URL = '/home/%s/%s/public_html/%s/%s' % (S3_USER, S3_BUCKET['bucket_name'], S3_BUCKET['app_dir'], PROJECT_SLUG)
        S3_DEPLOY_URL = '%s@%s:/home/%s/%s/public_html/%s/%s' % (S3_USER, S3_BUCKET['server_domain'], S3_USER, S3_BUCKET['bucket_name'], S3_BUCKET['app_dir'], PROJECT_SLUG)
        SERVERS = STAGING_SERVERS
        SERVER_BASE_URL = 'https://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DEBUG = True
        ASSETS_MAX_AGE = 20
    else:
        S3_BUCKET = None
        S3_BASE_URL = 'http://127.0.0.1:8000'
        S3_DEPLOY_URL = None
        SERVERS = []
        SERVER_BASE_URL = 'http://127.0.0.1:8001/%s' % PROJECT_SLUG
        SERVER_LOG_PATH = '/tmp'
        DEBUG = True
        ASSETS_MAX_AGE = 20

    DEPLOYMENT_TARGET = deployment_target

"""
Run automated configuration
"""
DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', None)

configure_targets(DEPLOYMENT_TARGET)
