# store_manager/settings.py

"""
## ملف إعدادات نهائي وجاهز للنشر (Production-Ready) ##
تمت إعادة هيكلته ليكون آمناً، ويدعم الملفات الثابتة والوسائط بشكل صحيح.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# --- 1. الإعدادات الأساسية وتحميل متغيرات البيئة ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# --- 2. الإعدادات الأمنية ---
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS_str = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_str.split(',')]

# --- 3. تعريف التطبيقات ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # <-- إضافة Whitenoise
    'django.contrib.staticfiles',
    'storages', # <-- إضافة django-storages
    'store',
]

# --- 4. البرمجيات الوسيطة (Middleware) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <-- تفعيل Whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'store_manager.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
WSGI_APPLICATION = 'store_manager.wsgi.application'

# --- 5. قاعدة البيانات (معتمدة على Supabase) ---
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# --- 6. التحقق من كلمة المرور والتدويل ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- 7. إعدادات الملفات الثابتة (Static Files) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # <-- إعداد Whitenoise

# --- 8. إعدادات ملفات الوسائط (Media Files) مع Supabase S3 ---
# هذا القسم سيقوم بتوجيه أي ملفات يتم رفعها (مثل صور المنتجات) إلى Supabase Storage
USE_S3 = os.getenv('USE_S3', 'False') == 'True'

if USE_S3:
    AWS_ACCESS_KEY_ID = os.getenv('SUPABASE_S3_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('SUPABASE_S3_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('SUPABASE_S3_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.getenv('SUPABASE_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = os.getenv('SUPABASE_S3_REGION_NAME')
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = 'public-read'
    AWS_LOCATION = 'media' # سيتم إنشاء مجلد media داخل الـ bucket
    
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    # الإعدادات الافتراضية للتطوير المحلي
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# --- 9. إعدادات أخرى ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')