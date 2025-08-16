#!/bin/bash
set -o errexit

# تحديث pip وتثبيت المتطلبات
pip install --upgrade pip
pip install -r requirements.txt

# ترحيل قاعدة البيانات
python manage.py migrate --noinput

# تجميع الملفات الثابتة
python manage.py collectstatic --noinput --clear
