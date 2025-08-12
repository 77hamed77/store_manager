# store/forms.py

from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        # نحدد الحقول التي ستظهر في الفورم
        fields = ['name', 'phone', 'address']
        
        # نحدد التسميات التي ستظهر بجانب كل حقل باللغة العربية
        labels = {
            'name': 'اسم العميل',
            'phone': 'رقم الهاتف (اختياري)',
            'address': 'العنوان (اختياري)',
        }
        
        # نحدد الأدوات (Widgets) لإضافة خصائص HTML مثل الكلاسات والتلميحات
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'مثال: محمد الأحمد',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'مثال: 0912345678',
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'مثال:  بجانب الجامع الشمالي ',
            }),
        }