"""
Django settings for dashboard_loader project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = ## Set in local settings file!!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'dashboard_loader',
    'dashboard_api',
    'widget_def',
    'widget_data',
#    'traffic_incident_loader',
#    'frontlineservice_uploader',
#    'rfs_loader',
#    'train_interruptions_loader',
#    'air_pollution_loader',
#    'twitter_loader',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dashboard_loader.urls'

WSGI_APPLICATION = 'dashboard_loader.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Sydney'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CELERYBEAT_SCHEDULE = {
    'poll_all_apps': {
            'task': 'dashboard_loader.tasks.update_all_apps',
            'schedule': datetime.timedelta(seconds=1),
            'args': (),
    },
}

# Allow tasks to run for up to 12 hours - Is there a smarter way
# to load the GTFS static data?
CELERYD_TASK_TIME_LIMIT = 60 * 60 * 12

LOGIN_URL="/login"
LOGOUT="/logout"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
LOCALROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."

STATIC_ROOT = LOCALROOT + '/static'
STATICFILES_DIRS = (
        LOCALROOT + '/dashboard_loader/static',
        )
STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        )
STATIC_URL = '/static/'

SESSION_COOKIE_PATH = '/'

ADMIN_SITE_URL = "/"

# TWITTER_API_KEY="KEY..."
# TWITTER_API_SECRET="SECRET..."
# TWITTER_ACCESS_TOKEN="TOKEN..."
# TWITTER_ACCESS_TOKEN_SECRET="TOKEN..."

