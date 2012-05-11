#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Diogo Pinheiro <diogormpinheiro@gmail.com>
##
## Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *

import os


# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native',
                        'HIGH_REPLICATION': True}
AUTOLOAD_SITECONF = 'indexes'

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
CACHE_MIDDLEWARE_SECONDS = 30

# PISTON SETTINGS
PISTON_DISPLAY_ERRORS = DEBUG
PISTON_EMAIL_ERRORS = "adriano@umitproject.org"
PISTON_STREAM_OUTPUT = DEBUG

ENVIRONMENT = os.environ.get('SERVER_SOFTWARE', '')
GAE = True
PRODUCTION = True
TEST = False

if ENVIRONMENT == '':
    GAE = False
elif ENVIRONMENT.startswith('Development'):
    PRODUCTION = False
elif ENVIRONMENT.startswith('GAETest'):
    TEST = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    'mediagenerator',
    #'djangologging',
    'protobuf',
    'piston',
    'messages',
    'agents',
    'geoip',
    'api',
    'gui',
    'reports',
    'suggestions',
    'events',
    'versions',
    'icm_tests',
    'twitter',
    'notificationsystem',
    'registration',
    'filetransfers',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
)

MIDDLEWARE_CLASSES = (
    'mediagenerator.middleware.MediaMiddleware',
    
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware', # CACHE
    #'django.middleware.csrf.CsrfViewMiddleware', # CSRF

    'django.middleware.common.CommonMiddleware', # CACHE
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'djangologging.middleware.LoggingMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.csrf',
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)
#Remove comment in the following line for v2 design
#TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates', 'v2'),)

ROOT_URLCONF = 'urls'

ROOT_MEDIA_FILTERS = {
    'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
    'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
}

YUICOMPRESSOR_PATH = os.path.join(os.path.dirname(__file__), 'yuicompressor-2.4.7.jar')

MEDIA_BUNDLES = (
     ('main.css',
        'css/main.css',
        'css/jquery-ui.css',
        'css/realtimebox.css', ),
     ('main.js',
         {'filter': 'mediagenerator.filters.media_url.MediaURL'},
         'js/jquery.js',
         'js/jquery-ui.js',
         'js/date.format.js',
         'js/markerclusterer.js',
         'js/common.js',
         'js/realtimebox.js',
         'js/map.js',
         'js/suggestion.js',
         'js/events.js',),
     ('bootstrap.css',
         'bs/assets/css/bootstrap-responsive.css',
         'bs/assets/css/bootstrap.css',
          ),
     ('bootstrap.js',
         {'filter': 'mediagenerator.filters.media_url.MediaURL'},
          'bs/assets/js/jquery.js', #We already include bootstrap
          'bs/assets/js/bootstrap-transition.js',
          'bs/assets/js/bootstrap-alert.js',
          'bs/assets/js/bootstrap-modal.js',
          'bs/assets/js/bootstrap-dropdown.js',
          'bs/assets/js/bootstrap-scrollspy.js',
          'bs/assets/js/bootstrap-tab.js',
          'bs/assets/js/bootstrap-tooltip.js',
          'bs/assets/js/bootstrap-popover.js',
          'bs/assets/js/bootstrap-button.js',
          'bs/assets/js/bootstrap-collapse.js',
          'bs/assets/js/bootstrap-carousel.js',
          'bs/assets/js/bootstrap-typeahead.js',),
                 
)

MEDIA_DEV_MODE = DEBUG
DEV_MEDIA_URL = '/devmedia/'
PRODUCTION_MEDIA_URL = '/media/'

NOTIFICATION_SENDER = "notification@openmonitor.org"
NOTIFICATION_TO = "notification@openmonitor.org"
NOTIFICATION_REPLY_TO = "notification@openmonitor.org"

GLOBAL_MEDIA_DIRS = (os.path.join(os.path.dirname(__file__), 'media'),)

INTERNAL_IPS = ('127.0.0.1', 'localhost',)
LOGGING_OUTPUT_ENABLED = True


# add support to user profile
AUTH_PROFILE_MODULE = 'users.UserProfile'
ACCOUNT_ACTIVATION_DAYS = 30
LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
#'django.core.mail.backends.console.EmailBackend'

if on_production_server:
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'gmailusername@gmail.com'
    EMAIL_HOST_PASSWORD = 'xxxxxxx'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'gmailusername@gmail.com'
    SERVER_EMAIL = 'gmailusername@gmail.com'
else:
    # local
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    DEFAULT_FROM_EMAIL = 'webmaster@localhost'

USE_I18N = True

SITENAME = "OpenMonitor"

##################
# RESPONSE COUNTS
MAX_NETLIST_RESPONSE = 10
MAX_AGENTSLIST_RESPONSE = 5

#########################
# File Transfer settings
PREPARE_UPLOAD_BACKEND = 'filetransfers.backends.delegate.prepare_upload'
PRIVATE_PREPARE_UPLOAD_BACKEND = 'djangoappengine.storage.prepare_upload'
PUBLIC_PREPARE_UPLOAD_BACKEND = 'djangoappengine.storage.prepare_upload'
SERVE_FILE_BACKEND = 'djangoappengine.storage.serve_file'
PUBLIC_DOWNLOAD_URL_BACKEND = 'filetransfers.backends.base_url.public_download_url'
PUBLIC_DOWNLOADS_URL_BASE = '/data/'


# aggregator private key
RSAKEY_MOD = 93740173714873692520486809225128030132198461438147249362129501889664779512410440220785650833428588898698591424963196756217514115251721698086685512592960422731696162410024157767288910468830028582731342024445624992243984053669314926468760439060317134193339836267660799899385710848833751883032635625332235630111
RSAKEY_EXP = 65537
RSAKEY_D = 62297015822781158796363618856389920569720490554603739852574703225696321267124285722204224123764419501867928817657919519054848555406464849450959012702348251941541095546410973524267691136995700233299378960173993986706088589136001011922024584878399897228054794884245267290619407261307654480907250669720474301281
RSAKEY_P = 7757705817565141349021648120631369992682141789699152399326127816192467211564791533199816990028647490792876630757010309393888042701542789312864387282715209
RSAKEY_Q = 12083491681603271568173938267128976608289124671971871656030565887109349091047806314688865045109296709421488821701923256321238599753290254378297945671005479
RSAKEY_U = 4807166779721366881723532650380832638823203637550840979310831953962905310688603113539132663918756964730460591047978835536521726443169772132990407509799218


RSA_KEYSIZE = 1024
