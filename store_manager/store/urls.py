# store/urls.py

from django.urls import path
from . import views

# app_name = 'store' # من الممارسات الجيدة تحديد اسم للتطبيق لتجنب تضارب الأسماء في المشاريع الكبيرة

urlpatterns = [
    # ===================================================================
    #   1. واجهات العرض الرئيسية (الصفحات التي يراها المستخدم)
    # ===================================================================
    # لوحة التحكم هي الصفحة الرئيسية للموقع
    path('', views.dashboard_view, name='dashboard'),
    
    # واجهة نقطة البيع التفاعلية
    path('pos/', views.pos_view, name='pos-view'),
    
    # صفحات القوائم والتقارير
    path('products/', views.product_list, name='product-list'),
    path('clients/', views.client_list, name='client-list'),
    path('reports/low-stock/', views.low_stock_report, name='low-stock-report'),
    
    # صفحة تفاصيل العميل (تستخدم ID العميل في الرابط)
    path('clients/<int:client_id>/', views.client_detail, name='client-detail'),

    # ===================================================================
    #   2. مسارات معالجة الإجراءات (Actions)
    # ===================================================================
    # هذا المسار يستقبل طلب POST لتسجيل دفعة ولا يعرض صفحة مباشرة
    path('clients/record-payment/<int:client_id>/', views.record_payment, name='record-payment'),
    
    # -- السطر التالي هو الذي تم إضافته لإصلاح الخطأ --
    # هذا المسار يقوم بتصدير تقرير النواقص كملف CSV
    path('reports/low-stock/export/', views.export_low_stock_csv, name='export-low-stock-csv'),


    # ===================================================================
    #   3. واجهات برمجة التطبيقات (API Endpoints for JavaScript)
    # ===================================================================
    # هذه المسارات ترجع بيانات بصيغة JSON لواجهة نقطة البيع
    path('api/search-products/', views.api_search_products, name='api-search-products'),
    path('api/search-clients/', views.api_search_clients, name='api-search-clients'),
    path('api/create-invoice/', views.api_create_invoice, name='api-create-invoice'),
    
    # صفحة تفاصيل العميل (تستخدم ID العميل في الرابط)
    path('clients/<int:client_id>/', views.client_detail, name='client-detail'),
    # مسار لصفحة إضافة عميل جديد
    path('clients/add/', views.client_form_view, name='client-add'),
    # مسار لصفحة تعديل عميل (يستخدم ID العميل)
    path('clients/<int:client_id>/edit/', views.client_edit_view, name='client-edit'),
    # مسار لصفحة تأكيد حذف العميل
    path('clients/<int:client_id>/delete/', views.client_delete_view, name='client-delete'),
]