from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
import asyncio
from BAKbot import bot, ADMIN_CHAT_ID
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aiogram import Bot
from .forms import OrderForm
from asgiref.sync import async_to_sync
from django.contrib import messages


ADMIN_CHAT_ID = '6618330710'  # Укажите ваш ID чата
bot = Bot(token='7621395982:AAEBUp892ayfVzC0o0ZZJcwOvUtjJCiRVDo')  # Укажите ваш токен бота


# Отправка уведомления в Telegram через безопасный вызов
async def send_telegram_message(message: str):
    try:
        await bot.send_message(ADMIN_CHAT_ID, message)
    except Exception as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")


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


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))  # Получаем количество из запроса

        print(f"Получен запрос на добавление: Продукт ID={product_id}, Количество={quantity}")

        cart_item, created = OrderItem.objects.get_or_create(
            user=request.user, product=product
        )
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        print(f"Обновлено: Продукт ID={product_id}, Количество в корзине={cart_item.quantity}")

        cart_count = OrderItem.objects.filter(user=request.user).count()
        return JsonResponse({'cart_count': cart_count})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def view_cart(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity
            })
            total += product.price * quantity
        except Product.DoesNotExist:
            pass  # Игнорируем несуществующие товары

    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})



def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart
    return redirect('cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')  # Перенаправление, если корзина пуста

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = sum(
                Product.objects.get(id=int(product_id)).price * quantity
                for product_id, quantity in cart.items()
            )
            order.save()

            # Очистка корзины после успешного оформления заказа
            request.session['cart'] = {}
            return redirect('order_success', order_id=order.id)

    else:
        form = OrderForm()

    cart_items = [
        {
            'product': Product.objects.get(id=int(product_id)),
            'quantity': quantity,
            'total_price': Product.objects.get(id=int(product_id)).price * quantity,
        }
        for product_id, quantity in cart.items()
    ]

    total = sum(item['total_price'] for item in cart_items)

    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    })

def order_success(request, order_id):
    return render(request, 'shop/order_success.html', {'order_id': order_id})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity
        })
        total += product.price * quantity
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})

