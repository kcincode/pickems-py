"""
WSGI config for pickems project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys
from whitenoise.django import DjangoWhiteNoise
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pickems.settings")

if 'OPENSHIFT' in os.environ:
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python2.7/site-packages')
    virtualenv = os.path.join(virtenv, 'bin/activate')

    try:
        execfile(virtualenv, dict(__file__=virtualenv))
    except IOError:
        pass

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
