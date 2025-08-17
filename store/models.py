# store/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

# ===================================================================
#   1. نماذج المنتجات والتصنيفات
# ===================================================================

class Category(models.Model):
    name = models.CharField(_("اسم التصنيف"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("تصنيف")
        verbose_name_plural = _("التصنيفات")
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(_("اسم القطعة"), max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("التصنيف"), related_name='products')
    sku = models.CharField(_("رمز القطعة/SKU"), max_length=100, unique=True, blank=True, null=True, db_index=True)
    
    purchase_price = models.DecimalField(_("سعر الشراء"), max_digits=10, decimal_places=2, default=0.0)
    sale_price = models.DecimalField(_("سعر البيع"), max_digits=10, decimal_places=2)
    
    stock_quantity = models.PositiveIntegerField(_("الكمية في المخزن"), default=0)
    reorder_level = models.PositiveIntegerField(_("حد إعادة الطلب"), default=5)

    class Meta:
        verbose_name = _("منتج")
        verbose_name_plural = _("المنتجات")
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_low_on_stock(self):
        """خاصية للتحقق بسهولة مما إذا كان المنتج على وشك النفاد."""
        return self.stock_quantity <= self.reorder_level

    def get_profit(self):
        """دالة لحساب الربح من بيع قطعة واحدة."""
        return self.sale_price - self.purchase_price

# ===================================================================
#   2. نماذج العملاء والديون
# ===================================================================

class Client(models.Model):
    name = models.CharField(_("اسم العميل"), max_length=150, db_index=True)
    phone = models.CharField(_("رقم الهاتف"), max_length=20, blank=True)
    address = models.CharField(_("العنوان"), max_length=250, blank=True)
    total_debt = models.DecimalField(_("إجمالي الدين"), max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = _("عميل")
        verbose_name_plural = _("العملاء")
        ordering = ['name']

    def __str__(self):
        return self.name

# ===================================================================
#   3. نماذج الفواتير والمدفوعات
# ===================================================================

class Invoice(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', _('نقدي')
        CREDIT = 'CREDIT', _('دين')

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("العميل"), related_name='invoices')
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    total_amount = models.DecimalField(_("المبلغ الإجمالي"), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_("طريقة الدفع"), max_length=10, choices=PaymentMethod.choices)

    class Meta:
        verbose_name = _("فاتورة")
        verbose_name_plural = _("الفواتير")
        ordering = ['-created_at']

    def __str__(self):
        client_name = self.client.name if self.client else _('زبون نقدي')
        return f"{_('فاتورة رقم')} {self.id} - {client_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name=_("الفاتورة"), related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("القطعة"), related_name='invoice_items')
    quantity = models.PositiveIntegerField(_("الكمية"))
    price_at_sale = models.DecimalField(_("السعر عند البيع"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("بند فاتورة")
        verbose_name_plural = _("بنود الفواتير")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_("العميل"), related_name='payments')
    amount = models.DecimalField(_("المبلغ المدفوع"), max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(_("تاريخ الدفع"), auto_now_add=True)
    notes = models.TextField(_("ملاحظات"), blank=True)

    class Meta:
        verbose_name = _("دفعة")
        verbose_name_plural = _("الدفعات")
        ordering = ['-payment_date']

    def __str__(self):
        # تم إصلاح الخطأ هنا: self. Amount أصبحت self.amount
        return f"{_('دفعة من')} {self.client.name} {_('بقيمة')} {self.amount}"

# ===================================================================
#   4. نماذج أخرى
# ===================================================================

class Note(models.Model):
    content = models.TextField(_("المحتوى"))
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    is_important = models.BooleanField(_("ملاحظة هامة"), default=False)

    class Meta:
        verbose_name = _("ملاحظة")
        verbose_name_plural = _("الملاحظات")
        ordering = ['-created_at']

    def __str__(self):
        return self.content[:50]