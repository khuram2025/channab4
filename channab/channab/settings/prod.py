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


AWS_ACCESS_KEY_ID = 'AKIASTSQA7RFKIXHUCWP '
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'channabdairy'
AWS_S3_SIGNATURE_NAME = 's3v4',
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL =  'public-read'
AWS_S3_VERITY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_LOCATION = 'static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_STORAGE_BUCKET_NAME, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
