"""
Django settings for smi project.
"""

import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
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

ALLOWED_HOSTS = [env("ALLOWED_HOSTS")]

# Application definition
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
]

LOCAL_APPS = [
    "events",
    "transductor",
    "measurement",
    "debouncers",
    "data_collector",
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smi.urls"

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

WSGI_APPLICATION = "smi.wsgi.application"

# Database
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": ("django.contrib.auth.password_validation" ".UserAttributeSimilarityValidator")},  # noqa
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": ("django.contrib.auth.password_validation" ".CommonPasswordValidator")},
    {"NAME": ("django.contrib.auth.password_validation" ".NumericPasswordValidator")},
]

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_L10N = True

# Static files (CSS, JavaScript, Images)
MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "media")

STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

## BUSINESS LOGIC VARIABLES
CONTRACTED_VOLTAGE = float(os.getenv("CONTRACTED_VOLTAGE", 220))

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    #     "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    #     "PAGE_SIZE": 10,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SIGE - Energy Management System",
    "DESCRIPTION": " SLAVE server - communication with energy transductors and data collection",
    "VERSION": "1.0.0",
}
