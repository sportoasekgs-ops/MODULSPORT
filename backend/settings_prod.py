import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', os.environ.get('SESSION_SECRET', 'CHANGE-THIS-IN-PRODUCTION'))

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ISERV_DOMAIN = os.environ.get('ISERV_DOMAIN', 'localhost')
ALLOWED_HOSTS = [ISERV_DOMAIN, f'*.{ISERV_DOMAIN}', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'backend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if os.environ.get('ISERV_AUTH_ENABLED', 'False') == 'True':
    MIDDLEWARE.insert(
        MIDDLEWARE.index('django.contrib.messages.middleware.MessageMiddleware'),
        'backend.middleware.iserv_auth.IServAuthMiddleware'
    )

ROOT_URLCONF = 'backend.main_urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'backend.wsgi.application'

db_engine = os.environ.get('DB_ENGINE', 'sqlite')

if db_engine == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'iserv_sportoase'),
            'USER': os.environ.get('DB_USER', 'sportoase'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

is_https = os.environ.get('HTTPS', 'True') == 'True'
CSRF_COOKIE_SECURE = is_https
SESSION_COOKIE_SECURE = is_https
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

ISERV_BASE_URL = os.environ.get('ISERV_BASE_URL', f'https://{ISERV_DOMAIN}')

CSRF_TRUSTED_ORIGINS = [
    ISERV_BASE_URL,
    'http://localhost:4200',
    'http://localhost:5000',
]

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    ISERV_BASE_URL,
    'http://localhost:4200',
    'http://127.0.0.1:4200',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

PERIOD_TIMES = {
    1: {'start': '08:00', 'end': '08:45'},
    2: {'start': '08:50', 'end': '09:35'},
    3: {'start': '09:55', 'end': '10:40'},
    4: {'start': '10:45', 'end': '11:30'},
    5: {'start': '11:50', 'end': '12:35'},
    6: {'start': '12:40', 'end': '13:25'},
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'sportoase.log',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'backend': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}
