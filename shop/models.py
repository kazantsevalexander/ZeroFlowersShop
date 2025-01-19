from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Связь с товаром
    quantity = models.PositiveIntegerField(default=1)  # Количество товаров
    delivery_address = models.TextField()  # Адрес доставки
    created_at = models.DateTimeField(auto_now_add=True)  # Дата заказа

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Связь с товаром
    quantity = models.PositiveIntegerField(default=1)  # Количество товаров

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.price
