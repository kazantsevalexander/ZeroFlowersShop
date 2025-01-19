from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from BAKbot import bot, ADMIN_CHAT_ID
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from django.contrib import messages
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

ADMIN_CHAT_ID = '6618330710'
TELEGRAM_BOT_TOKEN = '7621395982:AAEBUp892ayfVzC0o0ZZJcwOvUtjJCiRVDo'

def send_telegram_message_sync(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': ADMIN_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print(f"Сообщение успешно отправлено: {response.json()}")
    except requests.RequestException as e:
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
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user

            # Подсчет общей стоимости
            cart_items = []
            total_price = 0

            for product_id, quantity in cart.items():
                product = Product.objects.get(id=int(product_id))
                item_total = product.price * quantity
                total_price += item_total
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total_price': item_total
                })

            order.total_price = total_price
            order.save()

            # Формируем сообщение для Telegram
            message = f"🛍 Новый заказ #{order.id}\n\n"
            message += f"👤 Получатель: {order.recipient_name}\n"
            message += f"📞 Телефон: {order.phone}\n"
            message += f"📍 Адрес доставки: {order.delivery_address}\n"

            if order.comments:
                message += f"💬 Комментарий: {order.comments}\n"

            message += "\n📦 Товары:\n"

            for item in cart_items:
                message += f"- {item['product'].name} x{item['quantity']} = {item['total_price']}₽\n"

            message += f"\n💰 Общая сумма: {total_price}₽"
            message += f"\n📅 Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}"

            # Отправляем уведомление в Telegram используя новую функцию
            send_telegram_message_sync(message)

            # Очистка корзины после успешного оформления заказа
            request.session['cart'] = {}
            messages.success(request, 'Заказ успешно оформлен!')
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
    quantity = int(request.POST.get('quantity', 1))  # Получаем количество из формы

    cart = request.session.get('cart', {})

    # Если товар уже в корзине, увеличиваем количество, иначе добавляем с указанным числом
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity

    request.session['cart'] = cart
    request.session.modified = True  # Помечаем сессию как измененную

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
    total_price = 0
    total_quantity = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=int(product_id))
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity
        })
        total_price += product.price * quantity
        total_quantity += quantity  # Подсчет общего количества товаров

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total_price,
        'total_quantity': total_quantity  # Передаем общее количество
    })


@csrf_exempt
def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))

            cart = request.session.get('cart', {})
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
            request.session.modified = True

            # Пересчет итоговых значений
            total_price = sum(
                Product.objects.get(id=int(pid)).price * qty
                for pid, qty in cart.items()
            )
            total_quantity = sum(cart.values())

            return JsonResponse({
                'success': True,
                'total_quantity': total_quantity,
                'total_price': total_price
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)