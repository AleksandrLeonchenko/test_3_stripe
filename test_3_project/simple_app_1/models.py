from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings


class Item(models.Model):
    """
    Модель товара
    """
    CURRENCY_CHOICES = (
        (1, 'usd'),
        (2, 'rub'),
    )
    name = models.CharField(
        max_length=100
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    currency = models.IntegerField(
        null=True,
        choices=CURRENCY_CHOICES,
        default=1,
        verbose_name="Валюта"
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['pk']

    def get_currency_display(self):
        return dict(Item.CURRENCY_CHOICES)[self.currency]

    def __str__(self):
        return self.name




class Discount(models.Model):
    """
    Модель скидки на товар
    """
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
        ordering = ['pk']

    def __str__(self):
        return f"{self.amount}"


class Tax(models.Model):
    """
    Модель налога на товар
    """
    name = models.CharField(max_length=100)
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'
        ordering = ['pk']

    def __str__(self):
        return f"{self.rate}%"


class Order(models.Model):
    """
    Модель заказа
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    items = models.ManyToManyField(
        Item,
        related_name='orders'
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['pk']

    @property
    def total_price(self):
        total = 0
        for order_item in OrderItem.objects.filter(order=self):
            total += order_item.item.price * order_item.quantity

        if self.discount:
            total -= self.discount.amount

        if self.tax:
            total += (total * self.tax.rate / 100)

        return total


class OrderItem(models.Model):
    """
    Модель товаров в заказе
    """
    order = models.ForeignKey(
        Order,
        related_name='order_item',
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE
                             )
    quantity = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
        ordering = ['pk']

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
