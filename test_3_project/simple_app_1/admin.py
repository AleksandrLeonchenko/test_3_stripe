from django.contrib import admin

from .models import Item, Order, OrderItem


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description',
        'price',
    ]
    list_display_links = [
        'id',
        'name',
        'description',
        'price',
    ]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'item',
        'quantity',
    ]
    list_display_links = [
        'id',
        'order',
        'item',
        'quantity',
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem, OrderItemAdmin)

admin.site.site_title = 'Админ-панель test_3_project'
admin.site.site_header = 'Админ-панель test_3_project'
