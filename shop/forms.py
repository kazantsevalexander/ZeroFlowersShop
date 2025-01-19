from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['recipient_name', 'phone', 'delivery_address', 'comments']
        widgets = {
            'recipient_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'id': 'address', 'rows': 3}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'id': 'comments', 'rows': 2}),
        }
