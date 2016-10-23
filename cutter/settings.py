"""
Django settings for cutter project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n6c=i^%bnr%xyz=m&69matq=1d3k)9e-6daz+)6k+053!cqna9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['vm26173.hv8.ru', '80.78.251.208']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
    'bootstrapform',

    'cutter',
    'calc'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # # for django-pipeline
    # 'django.middleware.gzip.GZipMiddleware',
    # 'pipeline.middleware.MinifyHTMLMiddleware',
]

ROOT_URLCONF = 'cutter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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

WSGI_APPLICATION = 'cutter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tilecutter',
        'USER': 'tilecutteruser',
        'PASSWORD': 'graficon688028',
        'HOST': '127.0.0.1'
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = '/home/zeez/work/cutter/static/'

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), '../static', 'bower_components'),
    os.path.join(os.path.dirname(__file__), '../static'),
)

MEDIA_ROOT = "/root/webapps/cutter/media/"
MEDIA_URL = "/media/"


# STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

# for production
# STATICFILES_FINDERS = (
#     'pipeline.finders.FileSystemFinder',
#     'pipeline.finders.AppDirectoriesFinder',
#     'pipeline.finders.CachedFileFinder',
#     'pipeline.finders.PipelineFinder',
# )

# for develop
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE = {
    'PIPELINE_ENABLED': True,
    'COMPILERS': {
        'pipeline.compilers.stylus.StylusCompiler',
        'pipeline.compilers.es6.ES6Compiler',
    },
    'CSS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'STYLESHEETS': {
        # Project libraries.
        'libraries': {
            'source_filenames': (
                '/root/webapps/cutter/static/bower_components/bootstrap/dist/css/bootstrap.css',
            ),
            # Compress passed libraries and have
            # the output in`css/libs.min.css`.
            'output_filename': 'css/libs.min.css',
            # 'extra_context': {
            #     'media': 'screen,projection',
            # }
        }
        # ...
    },
    'JAVASCRIPT': {
        # Project JavaScript libraries.
        'libraries': {
            'source_filenames': (
                '/root/webapps/cutter/static/bower_components/jquery/dist/jquery.js',
            ),
            # Compress all passed files into `js/libs.min.js`.
            'output_filename': 'js/libs.min.js',
        }
        # ...
    }
}

# PIPELINE['CSS_COMPRESSOR'] = 'pipeline.compressors.NoopCompressor'
# PIPELINE['JS_COMPRESSOR'] = 'pipeline.compressors.NoopCompressor'

# DRAWING
DRAWING_WATERMARK_TEXT = "www.tilecutter.ru"
DRAWING_WATERMARK_FONT = "/root/webapps/cutter/static/fonts/arial.ttf"
