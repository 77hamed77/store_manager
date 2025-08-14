
# store/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ===================================================================
    #   1. واجهات العرض الرئيسية (الصفحات التي يراها المستخدم)
    # ===================================================================
    path('', views.dashboard_view, name='dashboard'),
    path('pos/', views.pos_view, name='pos-view'),
    path('products/', views.product_list, name='product-list'),
    path('clients/', views.client_list, name='client-list'),
    path('reports/low-stock/', views.low_stock_report, name='low-stock-report'),
    path('reports/profit/', views.profit_report_view, name='profit-report'),
    path('clients/<int:client_id>/', views.client_detail, name='client-detail'),

    # ===================================================================
    #   2. مسارات إدارة العملاء (CRUD) - تم التحديث
    # ===================================================================
    # مسار إضافة عميل جديد (يستخدم الدالة المدمجة)
    path('clients/add/', views.client_manage_view, name='client-add'),
    # مسار تعديل عميل (يستخدم نفس الدالة المدمجة)
    path('clients/<int:client_id>/edit/', views.client_manage_view, name='client-edit'),
    # مسار حذف العميل
    path('clients/<int:client_id>/delete/', views.client_delete_view, name='client-delete'),

    # ===================================================================
    #   3. مسارات معالجة الإجراءات (Actions)
    # ===================================================================
    path('clients/record-payment/<int:client_id>/', views.record_payment, name='record-payment'),
    path('reports/low-stock/export/', views.export_low_stock_csv, name='export-low-stock-csv'),

    # ===================================================================
    #   4. واجهات برمجة التطبيقات (API Endpoints for JavaScript)
    # ===================================================================
    path('api/search-products/', views.api_search_products, name='api-search-products'),
    path('api/search-clients/', views.api_search_clients, name='api-search-clients'),
    path('api/create-invoice/', views.api_create_invoice, name='api-create-invoice'),
]