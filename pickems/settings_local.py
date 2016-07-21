from pickems.settings import *
import sys

APP_URL = 'http://localhost:4200'
DEBUG = True
SECRET_KEY = 'random-asciiopmzw+$x^%_5+232-zhf$@fui*2$=ew4@1nab48$^!yn^d3)t*'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pickems_dev',
        'USER': 'root',
        'PASSWORD': 'secret',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

JWT_AUTH['JWT_SECRET_KEY'] = '0!sf@$-4^wyiwr%n%_8m+c9kf(u%r6*gl8csk+g)5g$-89w6=5'
