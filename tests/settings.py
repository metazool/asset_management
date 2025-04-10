from asset_management.settings import (
    INSTALLED_APPS,
    MIDDLEWARE,
    DATABASES,
    AUTH_USER_MODEL,
    REST_FRAMEWORK,
    ROOT_URLCONF,
)

# Use test secret key
SECRET_KEY = 'django-insecure-test-key-do-not-use-in-production'

# Use in-memory SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing to speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["null"],
            "level": "CRITICAL",
        },
    },
}

# Disable cache during tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Disable email sending during tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Use test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
