import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
LOG_PATH = BASE_DIR / "logs"
ENVFILE_PATH = BASE_DIR / "dev-env"

env = environ.Env()
env.read_env(str(ENVFILE_PATH))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SLAVE_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
if env("ENVIRONMENT") == "production":
    DEBUG = False

else:
    DEBUG = True

ALLOWED_HOSTS = ["*"] if DEBUG else [env("ALLOWED_HOSTS")]


# APPS
# ---------------------------------------------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
]

EXTERNAL_APPS = [
    "rest_framework",
    "drf_spectacular",
    "django_extensions",
    "django_filters",
    "debug_toolbar",
]

LOCAL_APPS = [
    "events",
    "transductor",
    "measurement",
    "debouncers",
    "data_collector",
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS


# MIDDLEWARE
# ---------------------------------------------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# TEMPLATE
# ---------------------------------------------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# DATABASES
# ---------------------------------------------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}


# PASSWORDS
# ---------------------------------------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": ("django.contrib.auth.password_validation" ".UserAttributeSimilarityValidator")},  # noqa
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": ("django.contrib.auth.password_validation" ".CommonPasswordValidator")},
    {"NAME": ("django.contrib.auth.password_validation" ".NumericPasswordValidator")},
]


# INTERNATIONALIZATION
# ---------------------------------------------------------------------------------------------------------------------
TIME_ZONE = "America/Sao_Paulo"

LOCALE_NAME = "pt_br"
LANGUAGE_CODE = "pt-br"
LANGUAGES = (
    ("en", "English"),
    ("pt-br", "Português"),
)

USE_I18N = True
USE_L10N = True
USE_TZ = True


# GENERAL CONFIGURATION
# ---------------------------------------------------------------------------------------------------------------------
ROOT_URLCONF = "sige_slave.urls"
WSGI_APPLICATION = "sige_slave.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Version 4.2 PKs will be big integers by defaul
APPEND_SLASH = True
LOGIN_REDIRECT_URL = "/"


# STATIC FILES AND MEDIA
# ---------------------------------------------------------------------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "media")
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)


# BUSINESS LOGIC VARIABLES
# ---------------------------------------------------------------------------------------------------------------------
CONTRACTED_VOLTAGE = float(os.getenv("CONTRACTED_VOLTAGE", 220))


# DJANGO REST FRAMEWORK
# ---------------------------------------------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 60,
}

# SPECTACULAR SETTINGS
# ---------------------------------------------------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "SIGE - Energy Management System",
    "DESCRIPTION": " SLAVE server - communication with energy transductors and data collection",
    "VERSION": "1.0.0",
    "DISABLE_ERRORS_AND_WARNINGS": True,
}


# LOGGING
# ---------------------------------------------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(module)-12s: %(message)s"},
        "middle": {"format": "%(module)-12s: [line: %(lineno)-3s] %(message)s"},
        "verbose": {
            "format": "%(asctime)s: %(module)-15s: %(message)s",
            "datefmt": "%d %b %Y - %H:%M:%S",
        },
    },
    "handlers": {
        "rich": {
            "class": "rich.logging.RichHandler",
            "formatter": "simple",
            "rich_tracebacks": True,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_PATH / "debug.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB rotative
            "formatter": "verbose",
        },
        "tasks-file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_PATH / "tasks" / "tasks.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB rotative
            "backupCount": 5,  # 5 files de backup de 10 MB cada
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "tasks": {
            "handlers": ["rich", "tasks-file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# DEBUG TOOLBAR
# ---------------------------------------------------------------------------------------------------------------------
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "INTERCEPT_REDIRECTS": False,
    "ALLOWED_HOSTS": ["localhost", "0.0.0.1"],
}
