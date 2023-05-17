from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'channab',
        'USER': 'khan',
        'PASSWORD': 'C@hannb183!',
        'HOST': 'localhost',
        'PORT': '',
    }
}
