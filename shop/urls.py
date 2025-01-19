from django.urls import path
from . import views
from .views import product_list

urlpatterns = [
    path('', product_list, name='product_list'),
    path('order/', views.place_order, name='place_order'),  # Проверь, что это добавлено
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

]
