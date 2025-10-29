# 🏪 Store Manager | نظام نقاط البيع وإدارة المخزون

**تطبيق ويب شامل تم تطويره باستخدام Django لحل مشكلة حقيقية: رقمنة وأتمتة العمليات اليومية للمتاجر الصغيرة. تم بناء هذا المشروع بحب لمساعدة والدي في الانتقال من السجلات الورقية إلى نظام رقمي فعال لإدارة المبيعات، المخزون، والديون.**

<!-- 🎬 VERY IMPORTANT: A GIF showing the POS interface, adding a product to the cart, and checking a customer's debt file would be incredibly powerful here. -->
<p align="center">
  <!-- <img src="path/to/your/store-manager-demo.gif" width="90%"> -->
</p>

---

### 🛠️ التقنيات المستخدمة (Tech Stack)

| Backend | Frontend | Database | Deployment |
| :---: | :---: | :---: | :---: |
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) | ![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white) |
| ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) | ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white) | ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white) | ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white) |
| | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white) (Dev) | |

---

### ✨ الميزات الرئيسية (Key Features)

- **📊 لوحة تحكم تفاعلية:** ملخص فوري للمبيعات اليومية، إجمالي الديون، والمنتجات التي تحتاج لإعادة التزويد.
- **🛒 نقطة بيع (POS) سريعة:** واجهة سهلة لإضافة المنتجات للسلة ودعم المبيعات النقدية والآجلة (الدين).
- **📦 إدارة متكاملة للمخزون:** نظام لإدارة المنتجات والفئات مع تتبع تلقائي للكميات بعد كل عملية بيع.
- **📒 نظام ديون احترافي:** ملف خاص لكل عميل مدين مع كشف حساب تفصيلي لجميع المعاملات.
- **🔔 إشعارات فورية عبر تليجرام:** تنبيهات تلقائية عند تسجيل دين جديد أو عند وصول منتج إلى حد النقص.

---

<details>
<summary>🚀 <strong>دليل الإعداد والتشغيل (Local Setup & Run)</strong></summary>

لتشغيل المشروع على جهازك المحلي، اتبع الخطوات التالية:

#### 1. استنساخ المستودع

git clone https://github.com/77hamed77/store_manager.git
cd store_manager
2. إعداد البيئة الافتراضية
code
Bash
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
3. تثبيت المكتبات المطلوبة
code
Bash
pip install -r requirements.txt
4. إعداد متغيرات البيئة
أنشئ ملف .env في جذر المشروع.
أضف المتغيرات الأساسية مثل SECRET_KEY و DEBUG.
أضف TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID لتفعيل الإشعارات.
5. تطبيق ترحيل قاعدة البيانات (Migrations)
code
Bash
python manage.py migrate
6. إنشاء حساب مدير (Superuser)
code
Bash
python manage.py createsuperuser
7. تشغيل الخادم
code
Bash
python manage.py runserver
الآن يمكنك الوصول إلى الموقع عبر الرابط: http://127.0.0.1:8000
</details>
<details>
<summary>☁️ <strong>إرشادات النشر على Render (Deployment Guide)</strong></summary>
تم إعداد هذا المشروع ليكون جاهزاً للنشر مباشرة على Render:
إنشاء خدمة ويب جديدة وربطها بمستودع GitHub.
إعدادات أوامر النشر:
Build Command: ./build.sh
Start Command: gunicorn store_manager.wsgi:application
إضافة متغيرات البيئة في لوحة تحكم Render، بما في ذلك DATABASE_URL من قاعدة بيانات PostgreSQL الخارجية (مثل Supabase).
</details>
🤝 المساهمة (Contributing)
المساهمات مرحب بها! يرجى اتباع الإجراءات القياسية لطلبات الدمج (Pull Requests).
📜 الترخيص (License)
