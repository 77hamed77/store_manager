# store_manager/settings.py

"""
## ملف إعدادات محسن واحترافي ##
تمت إعادة هيكلته ليكون آمناً وجاهزاً لبيئة التشغيل.
"""

import os
from pathlib import Path
from dotenv import load_dotenv # استيراد المكتبة

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---===> تحميل متغيرات البيئة من ملف .env <===---
load_dotenv(BASE_DIR / '.env')

# ===================================================================
#   1. الإعدادات الأمنية الأساسية
# ===================================================================

# قراءة المفتاح السري من متغيرات البيئة. هذا هو أهم تغيير أمني.
SECRET_KEY = os.getenv('SECRET_KEY')

# قراءة وضع التصحيح. os.getenv('DEBUG', 'False') == 'True' هي طريقة آمنة
# للتأكد من أن DEBUG يكون False ما لم يتم تعيينه صراحةً إلى True.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# قراءة النطاقات المسموح بها من متغير بيئة واحد مفصول بفاصلة.
ALLOWED_HOSTS_str = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_str.split(',')]


# ===================================================================
#   2. تعريف التطبيقات والبرمجيات الوسيطة
# ===================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store', # تطبيقك
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'], # من الأفضل تحديد مجلد قوالب مركزي
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


# ===================================================================
#   3. قاعدة البيانات
# ===================================================================
# هذا الإعداد مرن. عند النشر، يمكنك تعيين متغير DATABASE_URL
# لاستخدام PostgreSQL، وإلا فإنه سيعود إلى SQLite للتطوير المحلي.
import dj_database_url

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ===================================================================
#   4. التحقق من كلمة المرور والتدويل
# ===================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# تحسين: تغيير اللغة الافتراضية إلى العربية
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'UTC' # أفضل ممارسة: تخزين الوقت بـ UTC وعرضه بالمنطقة المحلية
USE_I18N = True
USE_TZ = True


# ===================================================================
#   5. الملفات الثابتة (Static Files)
# ===================================================================
STATIC_URL = 'static/'
# هذا المسار ضروري لأمر collectstatic عند النشر
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ===================================================================
#   6. إعدادات أخرى
# ===================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- إعدادات بوت التليجرام (تقرأ الآن بأمان من متغيرات البيئة) ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')