"""
Production settings for Heroku deployment
"""
import os
import dj_database_url
from decouple import config
from .settings import *

# Security Settings
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# Allowed Hosts
ALLOWED_HOSTS = [
    '.herokuapp.com',
    'exohuntappfirebase.web.app',
    'exohunt.biz',
    'www.exohunt.biz',
    'localhost',
    '127.0.0.1',
]

# CORS Settings for production - Allow frontend URLs
CORS_ALLOWED_ORIGINS = [
    'https://exohuntappfirebase.web.app',
    'https://exohunt.biz',
    'https://www.exohunt.biz',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# Allow all origins in development (remove in production if needed)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Database Configuration
# Use PostgreSQL on Heroku
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3'),
        conn_max_age=600
    )
}

# Static Files Configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}
