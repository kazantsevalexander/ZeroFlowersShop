from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, CartItem
from .forms import OrderForm
import asyncio
from bot import bot, ADMIN_CHAT_ID
from django.http import JsonResponse


def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user  # Привязка заказа к пользователю
            order.save()
            return redirect('product_list')  # Возвращаемся на главную
    else:
        form = OrderForm()
    return render(request, 'shop/place_order.html', {'form': form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Отправка уведомления в Telegram
            message = (
                f"Новый заказ!\n"
                f"Пользователь: {order.user.username}\n"
                f"Товар: {order.product.name}\n"
                f"Количество: {order.quantity}\n"
                f"Адрес доставки: {order.delivery_address}"
            )
            asyncio.run(bot.send_message(ADMIN_CHAT_ID, message))

            return redirect('product_list')
    else:
        form = OrderForm()
    return render(request, 'shop/place_order.html', {'form': form})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product
    )
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    # Подсчет количества товаров в корзине
    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count})

def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    return render(request, 'shop/view_cart.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')

def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == 'POST':
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                delivery_address=request.POST.get('delivery_address'),
            )
        cart_items.delete()
        return redirect('product_list')
    return render(request, 'shop/checkout.html', {'cart_items': cart_items})
