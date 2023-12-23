from django.db import models


class Item(models.Model):
    name = models.CharField(
        max_length=100
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


class Order(models.Model):
    items = models.ManyToManyField(
        Item,
        related_name='orders'
    )

    @property
    def total_price(self):
        total = 0
        for order_item in OrderItem.objects.filter(order=self):
            total += order_item.item.price * order_item.quantity
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
