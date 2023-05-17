from .base import *
ALLOWED_HOSTS = ['*']
DEBUG = True

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
