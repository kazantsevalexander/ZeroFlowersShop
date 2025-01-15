from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'quantity', 'delivery_address']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
        }