try:
    from .settings import *
except ImportError:
    pass

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "reset",
        "USER": "postgres",
        "PASSWORD": "bleubleu",
        "HOST": "postgres",
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 0,
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
}

DEFAULT_TEST_BROWSER = os.environ.get("TEST_BROWSER")

DEV_MODE = False

EMAIL_SUBJECT_PREFIX = "[TESTS] "

#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

# Monkey patch REST_FRAMEWORK settings to disable rate limit during tests
from .settings import REST_FRAMEWORK

del REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"]
del REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
