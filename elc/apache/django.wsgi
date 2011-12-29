import os
import sys

path = '/home/django'
if path not in sys.path:
    sys.path.append(path)

path = '/home/django/elc'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'elc.apache.settings_production'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
#from raven.contrib.django.middleware.wsgi import Sentry
#application = Sentry(django.core.handlers.wsgi.WSGIHandler())

print >> sys.stderr
