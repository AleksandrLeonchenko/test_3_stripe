from django.contrib import admin

from .models import Item


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


admin.site.register(Item, ItemAdmin)


admin.site.site_title = 'Админ-панель test_3_project'
admin.site.site_header = 'Админ-панель test_3_project'
