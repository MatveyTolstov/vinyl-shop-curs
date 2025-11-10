from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Genre,
    Artist,
    Product,
    Order,
    OrderItem,
    Review,
    ShippingAddress,
    Coupon,
)
from decimal import Decimal


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "genre_name", "description"]


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "artist_name", "country"]


class ProductSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(
        source="genre.get_genre_name_display", read_only=True
    )
    artist_name = serializers.CharField(source="artist.artist_name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "description",
            "price",
            "stock_quantity",
            "picture",
            "genre",
            "genre_name",
            "artist",
            "artist_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "id",
            "user",
            "full_name",
            "phone",
            "city",
            "address_line",
            "postal_code",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "discount_percent",
            "active",
            "valid_from",
            "valid_to",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "price_at_order",
            "subtotal",
        ]

    def get_subtotal(self, obj):
        return obj.price_at_order * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source="orderitem_set")
    total = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_name",
            "date_order",
            "status",
            "shipping_address",
            "coupon",
            "order_items",
            "total",
        ]
        read_only_fields = ["date_order"]


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    def get_total(self, obj):
        """Вычисляет общую сумму заказа"""
        total = Decimal("0")
        for item in obj.orderitem_set.all():
            total += item.price_at_order * Decimal(str(item.quantity))


        if hasattr(obj, "coupon") and obj.coupon and obj.coupon.active:
            discount_decimal = Decimal(str(obj.coupon.discount_percent)) / Decimal(
                "100"
            )
            total = total * (Decimal("1") - discount_decimal)

        return total


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "text",
            "user",
            "user_name",
            "product",
            "product_name",
            "created_at",
        ]
        read_only_fields = ["created_at", "user"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["date_joined"]


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class ShippingAddressInputSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    phone = serializers.CharField()
    city = serializers.CharField()
    address_line = serializers.CharField()
    postal_code = serializers.CharField()


class CheckoutSerializer(serializers.Serializer):
    shipping_address = ShippingAddressInputSerializer()
    coupon_code = serializers.CharField(required=False, allow_blank=True)


class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField()


class ProductFilterSerializer(serializers.Serializer):
    genre = serializers.IntegerField(required=False)
    artist = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    max_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    search = serializers.CharField(required=False)
