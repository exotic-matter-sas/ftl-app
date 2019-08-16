"""
Django settings for ftl project.

Generated by 'django-admin startproject' using Django 2.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import pathlib
from datetime import timedelta

from django.contrib.messages import constants as message_constants

from ftl.enums import FTLStorages, FTLPlugins

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q-2%l!knv+331nqu&ypc+gv&85nd$9*1g1max3692uxfu_!7w8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# This param allow app to run with an unbuilt frontend
DEV_MODE = False

# Custom user auth model
AUTH_USER_MODEL = 'core.FTLUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'mptt',
    'rest_framework',
    'webpack_loader',
    'ftl',
    'setup',
    'core',
    'frontend'
]

if DEBUG and DEV_MODE:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ftl.ftl_setup_middleware.FTLSetupMiddleware'
]
if DEBUG and DEV_MODE:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

ROOT_URLCONF = 'ftl.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'ftl', 'templates'),
                 os.path.join(BASE_DIR, 'core', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ftl.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'bleubleu',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/assets/'  # public path
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')  # internal path
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend', 'dist'),  # Webpack final bundle
    os.path.join(BASE_DIR, 'frontend', 'pdfjs'),
    os.path.join(BASE_DIR, 'frontend', 'src', 'assets'),
    os.path.join(BASE_DIR, 'ftl', 'static'),
)

# IPs allowed to see the debug toolbar app
INTERNAL_IPS = ['127.0.0.1']

# Login url used by @login_required decorator
LOGIN_URL = 'login'

# Redirect user to this url after login by default
LOGIN_REDIRECT_URL = '/app'

# Default settings for browser used for functional tests
DEFAULT_TEST_BROWSER = 'firefox'
TEST_BROWSER_HEADLESS = True

# Django Rest Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'core.models.FTLModelPermissions',
    ),
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1/second',
        'user': '15/second'
    }
}

# JWT API Token
# Docs: https://github.com/davesque/django-rest-framework-simplejwt#settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'STATS_FILE': os.path.join(BASE_DIR, 'frontend', 'webpack-stats.json'),
    }
}

ATOMIC_REQUESTS = True

# Workaround for configuring a preloaded Tika
os.environ['TIKA_SERVER_JAR'] = pathlib.Path(os.path.join(BASE_DIR, 'vendors', 'tika-server-1.20.jar')).as_uri()

# SMTP EMAIL SERVER conf
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'noreply@localhost.com'

# Customize MESSAGE_TAGS to match bootstrap alert classes
MESSAGE_TAGS = {
    message_constants.INFO: 'text-center alert alert-primary',
    message_constants.SUCCESS: 'text-center alert alert-success',
    message_constants.WARNING: 'text-center alert alert-warning',
    message_constants.ERROR: 'text-center alert alert-danger',
}

"""
DOCUMENT BINARY STORAGE
=======================
Remote storage requires:
    - extra settings (see EXTRA SETTINGS FOR STORAGE below)
    - extra Python module (see ftl.constants.FTLStorages docstring)
"""
DEFAULT_FILE_STORAGE = FTLStorages.FILE_SYSTEM

"""
DOCUMENT PROCESSING PLUGINS (order is important)
================================================
- Edit lines below to change enabled plugins
    - Optional plugins required to install additional Python modules
    - Most OCR plugins required a specific DEFAULT_FILE_STORAGE
    - Check ftl.constants.FTLplugins docstring to know what's required for the desired plugin 
- Only one plugin of each type should be enable at a time
"""
FTL_DOC_PROCESSING_PLUGINS = [
    # Extract text of non scanned documents (required)
    FTLPlugins.TEXT_EXTRACTION_TIKA,

    # Detect lang (required for search feature)
    FTLPlugins.LANG_DETECTOR_LANGID,

    # Search feature (required)
    FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR,
]

"""
EXTRA SETTINGS FOR REMOTE STORAGE OR OCR_GOOGLE_VISION_SYNC 
"""
# Additional settings required if you chose a remote storage
if DEFAULT_FILE_STORAGE == FTLStorages.AWS_S3:  # Amazon S3 storage
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_DEFAULT_ACL = 'private'
    S3_USE_SIGV4 = True
if DEFAULT_FILE_STORAGE == FTLStorages.GCS or FTLPlugins.OCR_GOOGLE_VISION_SYNC in FTL_DOC_PROCESSING_PLUGINS:
    import json
    from google.oauth2 import service_account

    credentials_raw = json.loads(os.environ.get('GCS_CREDENTIALS_CONTENT'))
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(credentials_raw)
    if DEFAULT_FILE_STORAGE == FTLStorages.GCS:
        GS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')

# ==================================================
# No settings under this line
# Auto import local `settings_local.py` if available
try:
    from .settings_local import *

    print('Local setting imported\n')
except ImportError as e:
    print(e)
    print('No local setting\n')
