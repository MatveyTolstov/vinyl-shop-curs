from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal


def max_len_choices(choices):
    return max(len(i) for i in choices)


class Genre(models.Model):
    class GenreChoices(models.TextChoices):
        ROCK_METAL = "rock and metal", "Рок & Металл"
        JAZZ_BLUES = "jazz and blues", "Джаз & Блюз"
        INDIE_ALTERNATIVE = "indie and alternative", "Инди & Альтернатива"
        POP_DISCO = "pop and disco", "Поп & Диско"
        CLASSICAL = "classical", "Классика"
        RUSSIAN_SOVIET = "russian and soviet", "Русское & Советское"

    genre_name = models.CharField(
        max_length=max_len_choices(GenreChoices.values), choices=GenreChoices.choices
    )
    description = models.TextField()

    def __str__(self):
        return self.get_genre_name_display()


class Artist(models.Model):
    artist_name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.artist_name


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    picture = models.ImageField(upload_to="products/images/", null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product_name", "artist")

    def __str__(self):
        return self.product_name


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "В обработке"),
        ("processing", "Обрабатывается"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_order = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    shipping_address = models.ForeignKey(
        "ShippingAddress", on_delete=models.SET_NULL, null=True, blank=True
    )
    coupon = models.ForeignKey(
        "Coupon", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_total(self):
        """Вычисляет общую сумму заказа"""
        total = Decimal("0")
        for item in self.orderitem_set.all():
            total += item.price_at_order * Decimal(str(item.quantity))

        if hasattr(self, "coupon") and self.coupon and self.coupon.active:
            discount_decimal = Decimal(str(self.coupon.discount_percent)) / Decimal(
                "100"
            )
            total = total * (Decimal("1") - discount_decimal)

        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"{self.quantity} of {self.product.product_name} in Order {self.order.id}"
        )


class Review(models.Model):
    rating = models.FloatField()
    text = models.TextField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.product_name} by {self.user.username}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    city = models.CharField(max_length=80)
    address_line = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name}, {self.city}, {self.address_line}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"


class LogEntry(models.Model):
    """Модель для хранения логов действий пользователей"""

    ACTION_CHOICES = [
        ("login", "Вход в систему"),
        ("logout", "Выход из системы"),
        ("signup", "Регистрация"),
        ("order_created", "Создан заказ"),
        ("order_updated", "Обновлен заказ"),
        ("product_viewed", "Просмотр товара"),
        ("cart_added", "Добавлено в корзину"),
        ("cart_removed", "Удалено из корзины"),
        ("review_created", "Создан отзыв"),
        ("coupon_applied", "Применен купон"),
        ("page_visited", "Посещение страницы"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_entries",
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_entries",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_entries",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Лог"
        verbose_name_plural = "Логи"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Анонимный"
        return f"{username} - {self.get_action_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class Favorite(models.Model):
    """Избранные товары пользователя"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        indexes = [
            models.Index(fields=["user", "product"]),
            models.Index(fields=["-created_at"]),
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"{self.user.username} → {self.product.product_name}"
