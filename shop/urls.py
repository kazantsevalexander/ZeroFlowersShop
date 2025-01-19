from django.urls import path
from . import views
from .views import product_list, checkout, order_success, view_cart, add_to_cart, remove_from_cart, update_cart

urlpatterns = [
    path('', product_list, name='product_list'),
    path('order/', views.place_order, name='place_order'),  # Проверь, что это добавлено
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='cart'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order-success/<int:order_id>/', order_success, name='order_success'),
    path('update-cart/<int:product_id>/', update_cart, name='update_cart'),
]
