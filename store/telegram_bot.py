# store/telegram_bot.py

import requests
import logging
from django.conf import settings

# الحصول على مسجل (logger) خاص بهذا الملف. هذه أفضل من استخدام print().
logger = logging.getLogger(__name__)

def send_telegram_message(message, fail_silently=True):
    """
    ترسل رسالة إلى محادثة التليجرام المحددة في الإعدادات.

    Args:
        message (str): النص المراد إرساله.
        fail_silently (bool): إذا كانت True، لن تسبب الدالة أي خطأ برمجي (exception) 
                              في حالة فشل الإرسال، بل ستسجل الخطأ فقط.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID غير معرف في settings.py. تم إلغاء إرسال الرسالة.")
        return

    # ملاحظة احترافية: هذه العملية متزامنة (Synchronous). في المشاريع الضخمة،
    # من الأفضل نقلها إلى عامل خلفية (Background Worker) مثل Celery
    # لتجنب إبطاء استجابة الموقع للمستخدم. لكنها ممتازة لهذا المشروع.

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=params, timeout=5)
        # التحقق من أن الطلب لم ينجح
        if response.status_code != 200:
            logger.error(
                "فشل إرسال رسالة تليجرام. رمز الحالة: %s، الرد: %s",
                response.status_code,
                response.text
            )
            # إذا لم تكن fail_silently، أثر الخطأ ليتم التعامل معه في مكان آخر
            if not fail_silently:
                response.raise_for_status()
    
    except requests.exceptions.RequestException as e:
        # هذا يلتقط أخطاء الشبكة مثل انقطاع الاتصال، فشل DNS، إلخ.
        logger.error("حدث خطأ في الشبكة عند محاولة إرسال رسالة تليجرام: %s", e)
        if not fail_silently:
            raise