# store/admin.py

from django.contrib import admin
from .models import (
    Category, Product, Client, Note, 
    Invoice, InvoiceItem, Payment
)

# ===================================================================
#   إعدادات واجهة الأدمن
# ===================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sale_price', 'stock_quantity', 'is_low_on_stock')
    list_filter = ('category', 'stock_quantity')
    search_fields = ('name', 'sku')
    list_per_page = 25

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'total_debt')
    search_fields = ('name', 'phone')
    list_per_page = 25

# --- إعدادات عرض الفواتير وبنودها ---

class InvoiceItemInline(admin.TabularInline):
    """
    لعرض بنود الفاتورة بشكل مدمج داخل صفحة الفاتورة نفسها.
    """
    model = InvoiceItem
    extra = 0  # لمنع عرض حقول فارغة إضافية
    readonly_fields = ('product', 'quantity', 'price_at_sale') # منع تعديل سجلات البيع التاريخية
    can_delete = False # منع حذف بنود من فاتورة مسجلة

    def has_add_permission(self, request, obj=None):
        return False # منع إضافة بنود جديدة من واجهة الأدمن

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'payment_method', 'total_amount', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('id', 'client__name')
    date_hierarchy = 'created_at' # لإضافة فلتر زمني هرمي
    inlines = [InvoiceItemInline]
    list_per_page = 25

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('client', 'amount', 'payment_date')
    list_filter = ('payment_date',)
    search_fields = ('client__name',)
    date_hierarchy = 'payment_date'
    list_per_page = 25

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_at', 'is_important')
    list_filter = ('is_important', 'created_at')

# ===================================================================
#   تخصيص عناوين لوحة التحكم
# ===================================================================
admin.site.site_header = "لوحة تحكم إدارة المحل"
admin.site.site_title = "نظام المحل"
admin.site.index_title = "مرحباً بك في نظام الإدارة"