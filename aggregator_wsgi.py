SITE_DIR = '/om'
import site
site.addsitedir(SITE_DIR)

import os
import sys
sys.path.append(SITE_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django.core.handlers.wsgi

import djcelery
djcelery.setup_loader()

application = django.core.handlers.wsgi.WSGIHandler()
