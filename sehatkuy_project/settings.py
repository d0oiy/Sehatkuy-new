"""
Django settings for sehatkuy_project project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-4_+vx3%uwzxut#&h8hfopiu2w32b6b2n^w4jvn4vv85l(@y#7x'

DEBUG = True

ALLOWED_HOSTS = ['*']


# ==============================
# APPLICATIONS
# ==============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Apps
    'home',
    'users',
    'consultation',
    'adminpanel',
    'doctors',
    'poliklinik',
    'appointments',
    'pharmacy',
    'articles',
    'laboratory',
    'emergency',

    # Third party
    'rest_framework',
    'corsheaders',
]


# ==============================
# MIDDLEWARE
# ==============================
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


ROOT_URLCONF = 'sehatkuy_project.urls'


# ==============================
# TEMPLATES
# ==============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'sehatkuy_project.wsgi.application'


# ==============================
# DATABASE
# ==============================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE"),
        "USER": os.environ.get("MYSQLUSER"),
        "PASSWORD": os.environ.get("MYSQLPASSWORD"),
        "HOST": os.environ.get("MYSQLHOST"),
        "PORT": os.environ.get("MYSQLPORT"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}



# ==============================
# PASSWORD VALIDATION
# ==============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================
# INTERNATIONALIZATION
# ==============================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Asia/Makassar"

USE_I18N = True

USE_TZ = True


# ==============================
# STATIC FILES
# ==============================
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# ==============================
# AUTH SETTINGS
# ==============================
AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/patient/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'

# ⭐ FIX UTAMA: IZINKAN LOGOUT VIA GET (DJANGO 5)
LOGOUT_VIEW_ALLOW_GET = True


# ==============================
# SECURITY (DEV MODE SAFE)
# ==============================
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]


# ==============================
# API & CORS
# ==============================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


# ==============================
# MEDIA
# ==============================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

GOOGLE_MAPS_API_KEY = "ISI_DENGAN_API_KEY_ANDA"


# ==============================
# IPAYMU SANDBOX / PAYMENT CONFIG
# ==============================
IPAYMU_SANDBOX = True
IPAYMU_API_KEY = os.environ.get('IPAYMU_API_KEY', 'SANDBOX9910ADFD-D8D3-4C8D-BFB5-20B8C21450EE')
IPAYMU_VA = os.environ.get('IPAYMU_VA', '0000005267071757')
# Default sandbox API endpoint (override via env if needed)
IPAYMU_API_URL = os.environ.get('IPAYMU_API_URL', 'https://sandbox.ipaymu.com/api/v2/payment')
# Optional secret used to sign requests (use a dedicated secret in production)
IPAYMU_API_SECRET = os.environ.get('IPAYMU_API_SECRET', IPAYMU_API_KEY)

# ==============================
# DEFAULT FIELD TYPE
# ==============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
