#!/bin/bash
set -o errexit

# تحديث pip وتثبيت المتطلبات
pip install --upgrade pip
pip install -r requirements.txt

# إصلاح تعارض numpy و onnxruntime إذا كان مستخدمًا
pip uninstall -y numpy onnxruntime || true
pip install numpy==1.24.4 onnxruntime==1.17.1

# ترحيل قاعدة البيانات
python manage.py migrate --noinput

# تجميع الملفات الثابتة
python manage.py collectstatic --noinput --clear
