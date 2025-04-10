# config/settings/local.py

from .base import *
import os
from dotenv import load_dotenv

load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sqxxvx=ik(#s@!)h*it5*@6^nck$4obi#%uxa9#=197d=pur74'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        "OPTIONS": {"driver": "ODBC Driver 18 for SQL Server", }
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Email settings for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "shubhamjadhav190@gmail.com"
EMAIL_HOST_PASSWORD = "odei empj myvi wfko"

ALLOWED_HOSTS=['viable-reasonably-goldfish.ngrok-free.app', 'localhost','coding1.questplus.in','coding2.questplus.in']
CSRF_TRUSTED_ORIGINS=['https://viable-reasonably-goldfish.ngrok-free.app','http://localhost:3000','https://coding1.questplus.in','https://coding2.questplus.in']
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ENC_KEY = os.getenv("ENC_KEY", "4k2bv6CRCbCYoVM9CfpIzjh2slagTK5N")

QuestApi = "https://api.questplus.in/"
QuestWeb = "https://admin.questplus.in/"