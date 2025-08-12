# store/views.py

# --- 1. استيراد المكتبات الأساسية ---
import json
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation # تحسين: استخدام Decimal للأموال

# --- 2. استيراد مكونات Django ---
from django.contrib import messages # تحسين: لإظهار رسائل للمستخدم
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, F, Sum, Max, Value, CharField, Case, When
from django.db.models.functions import Greatest, Coalesce
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _

# --- 3. استيراد النماذج والتوابع المحلية ---
from .models import Category, Product, Client, Invoice, InvoiceItem, Payment, Note
from .forms import ClientForm
from .telegram_bot import send_telegram_message

# --------------------------------------------------------------------------
# القسم الأول: واجهات العرض الرئيسية (الصفحات التي يراها المستخدم)
# --------------------------------------------------------------------------

def dashboard_view(request):
    """
    يعرض لوحة التحكم الرئيسية مع ملخص شامل ومحسن لحالة المحل.
    """
    # معالجة إضافة ملاحظة جديدة تتم فقط عند طلب POST
    if request.method == 'POST':
        note_content = request.POST.get('note_content')
        is_important = request.POST.get('is_important') == 'on'
        if note_content:
            Note.objects.create(content=note_content, is_important=is_important)
            messages.success(request, _("تمت إضافة الملاحظة بنجاح."))
        return redirect('dashboard')

    today = timezone.now().date()
    
    # تحسين: استخدام select_related و prefetch_related لتقليل استعلامات قاعدة البيانات
    today_invoices = Invoice.objects.filter(created_at__date=today)
    daily_sales_total = today_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    daily_invoice_count = today_invoices.count()

    debtor_clients = Client.objects.filter(total_debt__gt=0)
    total_debt_sum = debtor_clients.aggregate(total=Sum('total_debt'))['total'] or 0
    top_debtors = debtor_clients.order_by('-total_debt')[:5]

    top_low_stock = Product.objects.filter(stock_quantity__lte=F('reorder_level')).order_by('stock_quantity')[:5]
    
    recent_notes = Note.objects.order_by('-created_at')[:5]

    context = {
        'daily_sales_total': daily_sales_total,
        'daily_invoice_count': daily_invoice_count,
        'total_debt_sum': total_debt_sum,
        'top_debtors': top_debtors,
        'top_low_stock': top_low_stock,
        'recent_notes': recent_notes,
    }
    return render(request, 'store/dashboard.html', context)


def product_list(request):
    """
    يعرض قائمة بالمنتجات مع تحسينات في الأداء.
    """
    search_query = request.GET.get('q', "")
    selected_category_id = request.GET.get('category', "")

    # تحسين: استخدام select_related يقلل من عدد الاستعلامات عند الوصول للتصنيف
    product_queryset = Product.objects.select_related('category').order_by('name')

    if search_query:
        product_queryset = product_queryset.filter(
            Q(name__icontains=search_query) | Q(sku__icontains=search_query)
        )
    if selected_category_id:
        product_queryset = product_queryset.filter(category_id=selected_category_id)

    paginator = Paginator(product_queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'categories': categories,
        'selected_category': selected_category_id,
    }
    return render(request, 'store/product_list.html', context)


def client_list(request):
    """
    يعرض قائمة بكل العملاء مع ترتيبهم حسب آخر تعامل.
    """
    search_query = request.GET.get('q', "")
    
    clients_queryset = Client.objects.all()
    
    if search_query:
        clients_queryset = clients_queryset.filter(
            Q(name__icontains=search_query) | Q(phone__icontains=search_query)
        )

    total_debt_sum = Client.objects.filter(total_debt__gt=0).aggregate(total=Sum('total_debt'))['total'] or 0
    
    # تحسين: استخدام تاريخ قديم جداً كقيمة افتراضية للتعامل مع العملاء الجدد
    default_date = datetime(1900, 1, 1, tzinfo=timezone.get_current_timezone())

    clients_with_last_transaction = clients_queryset.annotate(
        last_invoice_date=Coalesce(Max('invoices__created_at'), Value(default_date)),
        last_payment_date=Coalesce(Max('payments__payment_date'), Value(default_date))
    ).annotate(
        last_transaction_date=Greatest('last_invoice_date', 'last_payment_date')
    ).order_by('-last_transaction_date')

    context = {
        'clients': clients_with_last_transaction,
        'total_debt_sum': total_debt_sum,
        'search_query': search_query,
    }
    return render(request, 'store/client_list.html', context)


def client_detail(request, client_id):
    """
    ## تحسين كبير في الأداء ##
    يعرض كشف حساب احترافي لعميل معين بطلب واحد فقط من قاعدة البيانات.
    """
    client = get_object_or_404(Client, id=client_id)
    
    # 1. جلب الفواتير كحركات
    invoices = client.invoices.annotate(
        type=Value('invoice', output_field=CharField()),
        date=F('created_at'),
        description=F('id'), # سيتم تنسيقه لاحقاً
        debit=F('total_amount'),
        credit=Value(Decimal('0.00'))
    ).values('type', 'date', 'description', 'debit', 'credit')

    # 2. جلب المدفوعات كحركات
    payments = client.payments.annotate(
        type=Value('payment', output_field=CharField()),
        date=F('payment_date'),
        description=F('notes'),
        debit=Value(Decimal('0.00')),
        credit=F('amount')
    ).values('type', 'date', 'description', 'debit', 'credit')

    # 3. دمج الحركتين في طلب واحد مرتب من قاعدة البيانات مباشرة
    transactions = invoices.union(payments).order_by('date')

    # 4. حساب الرصيد المتحرك في Python (هذه الخطوة سريعة الآن)
    running_balance = 0
    transactions_with_balance = []
    for tx in transactions:
        running_balance += tx['debit'] - tx['credit']
        tx['balance_after'] = running_balance
        transactions_with_balance.append(tx)
    
    transactions_with_balance.reverse()

    context = {
        'client': client,
        'transactions_with_balance': transactions_with_balance
    }
    return render(request, 'store/client_detail.html', context)


def low_stock_report(request):
    search_query = request.GET.get('q', "")
    sort_by = request.GET.get('sort_by', 'deficit')

    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('reorder_level')
    ).annotate(
        deficit=F('reorder_level') - F('stock_quantity')
    )

    if search_query:
        low_stock_products = low_stock_products.filter(
            Q(name__icontains=search_query) | Q(sku__icontains=search_query)
        )

    # تحسين: جعل الفرز أكثر مرونة
    order_field = '-deficit'
    if sort_by == 'name':
        order_field = 'name'
    elif sort_by == 'stock':
        order_field = 'stock_quantity'
    
    low_stock_products = low_stock_products.order_by(order_field)
    
    context = {
        'products': low_stock_products,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'store/low_stock_report.html', context)


def pos_view(request):
    return render(request, 'store/pos.html')


# --------------------------------------------------------------------------
# القسم الثاني: دوال معالجة الإجراءات وتصدير البيانات
# --------------------------------------------------------------------------

@require_POST
@transaction.atomic
def record_payment(request, client_id):
    """
    ## تحسين أمني ##
    تسجل دفعة جديدة من عميل باستخدام Decimal بدلاً من float.
    """
    client = get_object_or_404(Client, id=client_id)
    amount_str = request.POST.get('amount')
    notes = request.POST.get('notes')

    if amount_str:
        try:
            # استخدام Decimal لضمان الدقة المالية
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError("المبلغ يجب أن يكون أكبر من صفر.")
            
            Payment.objects.create(client=client, amount=amount, notes=notes)
            client.total_debt -= amount
            client.save()
            messages.success(request, _("تم تسجيل الدفعة بنجاح."))
        
        except (ValueError, InvalidOperation):
            messages.error(request, _("الرجاء إدخال مبلغ صحيح."))

    return redirect('client-detail', client_id=client_id)


def export_low_stock_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="low_stock_report.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    writer.writerow([_('اسم المنتج'), _('الكمية المتبقية'), _('حد إعادة الطلب'), _('مقدار النقص')])

    products = Product.objects.filter(stock_quantity__lte=F('reorder_level')).annotate(
        deficit=F('reorder_level') - F('stock_quantity')
    ).order_by('-deficit')
    
    for product in products:
        writer.writerow([product.name, product.stock_quantity, product.reorder_level, product.deficit])
    
    return response


# --------------------------------------------------------------------------
# القسم الثالث: واجهات برمجة التطبيقات (API Endpoints for JavaScript)
# --------------------------------------------------------------------------

def api_search_products(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)
        
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query),
        stock_quantity__gt=0
    )[:10]
    
    results = [{'id': p.id, 'name': p.name, 'price': str(p.sale_price), 'stock': p.stock_quantity} for p in products]
    return JsonResponse(results, safe=False)


def api_search_clients(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)

    clients = Client.objects.filter(name__istartswith=query)[:10]
    results = [{'id': c.id, 'name': c.name} for c in clients]
    return JsonResponse(results, safe=False)


@csrf_exempt
@require_POST
@transaction.atomic
def api_create_invoice(request):
    """
    ## تحسين كبير في الأداء والأمان ##
    API لإنشاء فاتورة جديدة، مع تقليل استعلامات قاعدة البيانات ومعالجة الأخطاء بشكل أفضل.
    """
    try:
        data = json.loads(request.body)
        cart_items = data.get('cart', [])
        payment_method = data.get('payment_method')
        client_id = data.get('client_id')

        if not cart_items or not payment_method:
            return JsonResponse({'status': 'error', 'message': _('بيانات ناقصة')}, status=400)

        total_amount = sum(Decimal(item['price']) * int(item['quantity']) for item in cart_items)
        
        client = None
        if payment_method == 'CREDIT':
            if not client_id:
                return JsonResponse({'status': 'error', 'message': _('يجب تحديد عميل للبيع بالدين')}, status=400)
            client = get_object_or_404(Client, id=client_id)

        invoice = Invoice.objects.create(
            client=client, total_amount=total_amount, payment_method=payment_method
        )

        # تحسين الأداء: جلب كل المنتجات في طلب واحد (N+1 Fix)
        product_ids = [item['id'] for item in cart_items]
        products = Product.objects.in_bulk(product_ids) # in_bulk أسرع للبحث بالـ ID

        invoice_items_to_create = []
        products_to_update = []

        for item in cart_items:
            product = products.get(item['id'])
            if not product:
                raise Product.DoesNotExist(f"المنتج برقم ID {item['id']} غير موجود.")
            
            quantity_sold = int(item['quantity'])
            if product.stock_quantity < quantity_sold:
                raise ValueError(f"كمية غير كافية للمنتج: {product.name}")
            
            invoice_items_to_create.append(
                InvoiceItem(invoice=invoice, product=product, quantity=quantity_sold, price_at_sale=Decimal(item['price']))
            )

            was_low_on_stock = product.is_low_on_stock
            product.stock_quantity -= quantity_sold
            products_to_update.append(product)
            
            # إرسال إشعار فقط عند عبور حد النقص
            if not was_low_on_stock and product.is_low_on_stock:
                try:
                    message = f"📉 *نقص في المخزون* 📉\n\nالمنتج: *{product.name}*\nالكمية المتبقية: *{product.stock_quantity}*"
                    send_telegram_message(message)
                except Exception as e:
                    print(f"فشل إرسال إشعار نقص المخزون: {e}") # لا نوقف العملية بسبب فشل الإشعار

        InvoiceItem.objects.bulk_create(invoice_items_to_create)
        Product.objects.bulk_update(products_to_update, ['stock_quantity'])

        if client:
            client.total_debt += total_amount
            client.save()
            try:
                message = f"🚨 *دين جديد* 🚨\n\nالعميل: *{client.name}*\nمبلغ الفاتورة: *{total_amount:.2f}*\nإجمالي الدين الحالي: *{client.total_debt:.2f}*"
                send_telegram_message(message)
            except Exception as e:
                print(f"فشل إرسال إشعار الدين الجديد: {e}")

        return JsonResponse({'status': 'success', 'message': _('تم إنشاء الفاتورة بنجاح!'), 'invoice_id': invoice.id})

    except (Client.DoesNotExist, Product.DoesNotExist) as e:
        return JsonResponse({'status': 'error', 'message': _('عنصر مطلوب غير موجود.')}, status=404)
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        print(f"An unexpected error occurred in api_create_invoice: {e}")
        return JsonResponse({'status': 'error', 'message': _('حدث خطأ غير متوقع في الخادم.')}, status=500)


# --------------------------------------------------------------------------
# القسم الرابع: دوال إدارة العملاء (إضافة - تعديل - حذف)
# --------------------------------------------------------------------------

def client_manage_view(request, client_id=None):
    """
    ## تحسين الكود (DRY) ##
    دالة واحدة ذكية لمعالجة إضافة وتعديل العملاء.
    """
    instance = None
    if client_id:
        instance = get_object_or_404(Client, id=client_id)
        page_title = _('تعديل بيانات عميل')
    else:
        page_title = _('إضافة عميل جديد')

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم حفظ بيانات العميل بنجاح.'))
            return redirect('client-list')
    else:
        form = ClientForm(instance=instance)

    context = {
        'form': form,
        'page_title': page_title,
        'instance': instance
    }
    return render(request, 'store/client_form.html', context)


def client_delete_view(request, client_id):
    """
    تعالج حذف عميل بعد التأكيد.
    """
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        messages.success(request, _(f'تم حذف العميل "{client_name}" بنجاح.'))
        return redirect('client-list')
    
    context = {
        'client': client
    }
    return render(request, 'store/client_confirm_delete.html', context)