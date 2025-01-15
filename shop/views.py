from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order
from .forms import OrderForm
import asyncio
from bot import bot, ADMIN_CHAT_ID


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
