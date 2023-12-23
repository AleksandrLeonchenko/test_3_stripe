from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings


class Item(models.Model):
    name = models.CharField(
        max_length=100
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


class Discount(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.amount}"


class Tax(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    def __str__(self):
        return f"{self.rate}%"


class Order(models.Model):
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

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
