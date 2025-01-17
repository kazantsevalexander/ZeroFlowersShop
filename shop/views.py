from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, CartItem
import asyncio
from BAKbot import bot, ADMIN_CHAT_ID
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aiogram import Bot
from .forms import OrderForm
from asgiref.sync import async_to_sync

ADMIN_CHAT_ID = '6618330710'  # Укажите ваш ID чата
bot = Bot(token='7621395982:AAEBUp892ayfVzC0o0ZZJcwOvUtjJCiRVDo')  # Укажите ваш токен бота


# Отправка уведомления в Telegram через безопасный вызов
async def send_telegram_message(message: str):
    try:
        await bot.send_message(ADMIN_CHAT_ID, message)
    except Exception as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")


def product_list(request):
    # Получение всех продуктов
    products = Product.objects.all()

    # Получение данных корзины для текущего пользователя
    cart_items = {}
    if request.user.is_authenticated:
        user_cart_items = CartItem.objects.filter(user=request.user)
        cart_items = {item.product.id: item.quantity for item in user_cart_items}

    return render(request, 'shop/product_list.html', {
        'products': products,
        'cart_items': cart_items  # Передача количества товаров в корзине
    })




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

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, product=product
        )
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        print(f"Обновлено: Продукт ID={product_id}, Количество в корзине={cart_item.quantity}")

        cart_count = CartItem.objects.filter(user=request.user).count()
        return JsonResponse({'cart_count': cart_count})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)

    # Передача полного списка элементов с их количеством
    return render(
        request,
        'shop/view_cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


def remove_from_cart(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('product_list')  # Перенаправление, если корзина пуста

    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address')
        if delivery_address:
            total_price = 0
            order_details = []  # Очищаем, чтобы избежать дублирования

            for item in cart_items:
                # Создание заказа на основе корзины
                Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    delivery_address=delivery_address,
                )
                total_price += item.quantity * item.product.price
                # Добавляем строку с количеством и итоговой ценой за товар
                order_details.append(
                    f"• {item.product.name} × {item.quantity} шт. — {item.quantity * item.product.price:.2f} BYN"
                )

            # Очистка корзины после оформления заказа
            cart_items.delete()

            # Формирование сообщения для Telegram
            message = (
                f"🌸 НОВЫЙ ЗАКАЗ!\n\n"
                f"👤 Получатель: {request.POST['recipient_name']}\n"
                f"📱 Телефон: {request.POST['phone']}\n"
                f"📧 Email: {request.POST['email']}\n"
                f"📍 Адрес доставки: {request.POST['delivery_address']}\n"
                f"\n🛍️ СОСТАВ ЗАКАЗА:\n" +
                "\n".join(order_details) +
                f"\n\n💰 Итого к оплате: {total_price:.2f} BYN"
            )

            if request.POST.get('comments'):
                message += f"\n\n✏️ Комментарий к заказу:\n{request.POST['comments']}"

            # Отправляем сообщение в Telegram
            async_to_sync(send_telegram_message)(message)

            return redirect('product_list')  # Перенаправление на главную после заказа

    return render(request, 'shop/checkout.html', {'cart_items': cart_items})


