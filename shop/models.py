from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с пользователем
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Связь с товаром
    quantity = models.PositiveIntegerField(default=1)  # Количество товаров
    delivery_address = models.TextField()  # Адрес доставки
    created_at = models.DateTimeField(auto_now_add=True)  # Дата заказа

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"