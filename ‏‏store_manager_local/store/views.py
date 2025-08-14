# store/views.py

# --- 1. استيراد المكتبات الأساسية ---
import json
import csv
from datetime import datetime
from .forms import ClientForm

# --- 2. استيراد مكونات Django ---
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, F, Sum, Max, Value
from django.db.models.functions import Greatest, Coalesce
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt # <--- هذا هو السطر الذي تم إضافته

# --- 3. استيراد النماذج والتوابع المحلية ---
from .models import Category, Product, Client, Invoice, InvoiceItem, Payment, Note
from .telegram_bot import send_telegram_message

# --------------------------------------------------------------------------
# القسم الأول: واجهات العرض الرئيسية (الصفحات التي يراها المستخدم)
# --------------------------------------------------------------------------

def dashboard_view(request):
    if request.method == 'POST':
        note_content = request.POST.get('note_content')
        is_important = request.POST.get('is_important') == 'on'
        if note_content:
            Note.objects.create(content=note_content, is_important=is_important)
        return redirect('dashboard')

    today = timezone.now().date()
    
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
    search_query = request.GET.get('q', "")
    selected_category_id = request.GET.get('category', "")

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
    search_query = request.GET.get('q', "")
    
    clients_queryset = Client.objects.all()
    
    if search_query:
        clients_queryset = clients_queryset.filter(
            Q(name__icontains=search_query) | Q(phone__icontains=search_query)
        )

    total_debt_sum = Client.objects.filter(total_debt__gt=0).aggregate(total=Sum('total_debt'))['total'] or 0
    
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
    client = get_object_or_404(Client, id=client_id)
    
    invoices = client.invoices.all()
    payments = client.payments.all()
    
    transactions = []
    for inv in invoices:
        transactions.append({'date': inv.created_at, 'type': 'invoice', 'obj': inv})
    for pmt in payments:
        transactions.append({'date': pmt.payment_date, 'type': 'payment', 'obj': pmt})
    
    transactions.sort(key=lambda x: x['date'])

    running_balance = 0
    transactions_with_balance = []
    for tx in transactions:
        if tx['type'] == 'invoice':
            running_balance += tx['obj'].total_amount
            tx['description'] = f"فاتورة رقم {tx['obj'].id}"
            tx['amount'] = tx['obj'].total_amount
        else:
            running_balance -= tx['obj'].amount
            tx['description'] = "تسديد دفعة"
            tx['amount'] = tx['obj'].amount
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
    client = get_object_or_404(Client, id=client_id)
    amount_str = request.POST.get('amount')
    notes = request.POST.get('notes')

    if amount_str:
        amount = float(amount_str)
        Payment.objects.create(client=client, amount=amount, notes=notes)
        client.total_debt -= amount
        client.save()

    return redirect('client-detail', client_id=client_id)


def export_low_stock_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="low_stock_report.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    writer.writerow(['اسم المنتج', 'الكمية المتبقية', 'حد إعادة الطلب', 'مقدار النقص'])

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
    
    results = [{'id': p.id, 'name': p.name, 'price': p.sale_price, 'stock': p.stock_quantity} for p in products]
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
    try:
        data = json.loads(request.body)
        cart_items = data.get('cart', [])
        payment_method = data.get('payment_method')
        client_id = data.get('client_id')

        if not cart_items or not payment_method:
            return JsonResponse({'status': 'error', 'message': 'بيانات ناقصة'}, status=400)

        total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
        
        client = None
        if payment_method == 'CREDIT' and client_id:
            client = get_object_or_404(Client, id=client_id)

        invoice = Invoice.objects.create(
            client=client, total_amount=total_amount, payment_method=payment_method
        )

        products_to_update = []
        for item in cart_items:
            product = get_object_or_404(Product, id=item['id'])
            quantity_sold = int(item['quantity'])

            if product.stock_quantity < quantity_sold:
                raise ValueError(f"كمية غير كافية للمنتج: {product.name}")
            
            InvoiceItem.objects.create(
                invoice=invoice, product=product, quantity=quantity_sold, price_at_sale=float(item['price'])
            )

            is_already_low = product.is_low_on_stock
            product.stock_quantity -= quantity_sold
            products_to_update.append(product)
            
            if not is_already_low and product.is_low_on_stock:
                message = f"📉 *نقص في المخزون* 📉\n\nالمنتج: *{product.name}*\nالكمية المتبقية: *{product.stock_quantity}*"
                send_telegram_message(message)
        
        Product.objects.bulk_update(products_to_update, ['stock_quantity'])

        if client:
            client.total_debt += total_amount
            client.save()
            message = f"🚨 *دين جديد* 🚨\n\nالعميل: *{client.name}*\nمبلغ الفاتورة: *{total_amount:.2f}*\nإجمالي الدين الحالي: *{client.total_debt:.2f}*"
            send_telegram_message(message)

        return JsonResponse({'status': 'success', 'message': 'تم إنشاء الفاتورة بنجاح!', 'invoice_id': invoice.id})

    except (Client.DoesNotExist, Product.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'عنصر مطلوب غير موجود.'}, status=404)
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        print(f"An unexpected error occurred in api_create_invoice: {e}")
        return JsonResponse({'status': 'error', 'message': 'حدث خطأ غير متوقع في الخادم.'}, status=500)


# --------------------------------------------------------------------------
# القسم الرابع: دوال إدارة العملاء (إضافة - تعديل - حذف)
# --------------------------------------------------------------------------

def client_form_view(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client-list')
    else:
        form = ClientForm()

    context = {
        'form': form,
        'page_title': 'إضافة عميل جديد'
    }
    return render(request, 'store/client_form.html', context)


def client_edit_view(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client-list')
    else:
        form = ClientForm(instance=client)
    context = {
        'form': form,
        'page_title': f'تعديل بيانات: {client.name}'
    }
    return render(request, 'store/client_form.html', context)


def client_delete_view(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        client.delete()
        return redirect('client-list')
    context = {
        'client': client
    }
    return render(request, 'store/client_confirm_delete.html', context)