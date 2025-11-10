from django.contrib import admin
from .models import (
    Product,
    Genre,
    Artist,
    OrderItem,
    Order,
    Review,
    ShippingAddress,
    Coupon,
    LogEntry,
)



@admin.register(Artist, Genre, OrderItem, Order, Review, Coupon, ShippingAddress)
class ShopAdmin(admin.ModelAdmin):
    pass


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "created_at",
        "user",
        "action",
        "description",
        "ip_address",
    ]
    list_filter = ["action", "created_at", "user"]
    search_fields = ["description", "user__username", "ip_address"]
    readonly_fields = [
        "user",
        "action",
        "description",
        "ip_address",
        "user_agent",
        "order",
        "product",
        "created_at",
    ]
    date_hierarchy = "created_at"
    
    def has_add_permission(self, request):
        return False  # Запрещаем создание логов вручную
    
    def has_change_permission(self, request, obj=None):
        return False  # Запрещаем редактирование логов


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = [
        "product_name",
        "price",
        "genre",
        "artist",
    ]
    list_filter = ["genre", "artist"]
    search_fields = ["product_name"]


admin.site.register(Product, ProductAdmin)
