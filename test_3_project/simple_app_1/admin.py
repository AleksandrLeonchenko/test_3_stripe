from django.contrib import admin

from .models import Item, Order, OrderItem, Discount, Tax


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


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'discount',
        'tax',
    ]
    list_display_links = [
        'id',
        'user',
        'discount',
        'tax',
    ]


class DiscountAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'amount',
    ]
    list_display_links = [
        'id',
        'name',
        'amount',
    ]


class TaxAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'rate',
    ]
    list_display_links = [
        'id',
        'name',
        'rate',
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Tax, TaxAdmin)

admin.site.site_title = 'Админ-панель test_3_project'
admin.site.site_header = 'Админ-панель test_3_project'
