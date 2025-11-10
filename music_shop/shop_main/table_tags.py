from django import template

register = template.Library()


@register.filter
def table_to_url(table_name):
    mapping = {
        "Жанры": "genre",
        "Исполнители": "artist",
        "Товары (Пластинки)": "product",
        "Заказы": "order",
        "Элементы заказа": "orderitem",
        "Отзывы": "review",
        "Адреса доставки": "shippingaddress",
        "Промокоды": "coupon",
    }
    return mapping.get(table_name, "")


@register.filter
def table_to_model_name(table_name):
    mapping = {
        "Жанры": "Genre",
        "Исполнители": "Artist",
        "Товары (Пластинки)": "Product",
        "Заказы": "Order",
        "Элементы заказа": "OrderItem",
        "Отзывы": "Review",
        "Адреса доставки": "ShippingAddress",
        "Промокоды": "Coupon",
    }
    return mapping.get(table_name, "")
