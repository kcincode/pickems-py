from almanac.settings import *
import sys

APP_URL = 'http://localhost:4200'
DEBUG = True
SECRET_KEY = '+$^1k$ic!&eq!w7l#u&5k5^ob7sn8tdee41_+v!f%h*iv5!zr2'
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
