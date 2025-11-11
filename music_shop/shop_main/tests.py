from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from .logger_utils import create_log_entry
from .models import (
    Artist,
    Coupon,
    Genre,
    LogEntry,
    Order,
    OrderItem,
    Product,
)


class ModelStrTests(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(
            genre_name=Genre.GenreChoices.ROCK_METAL, description="desc"
        )
        self.artist = Artist.objects.create(artist_name="Deep Purple", country="UK")
        self.product = Product.objects.create(
            product_name="Perfect Strangers",
            description="Album",
            price=Decimal("99.99"),
            stock_quantity=10,
            genre=self.genre,
            artist=self.artist,
        )
        self.user = User.objects.create_user(username="alice", password="pass12345")

    def test_genre_str_returns_display_value(self):
        self.assertEqual(str(self.genre), "Рок & Металл")

    def test_artist_str(self):
        self.assertEqual(str(self.artist), "Deep Purple")

    def test_product_str(self):
        self.assertEqual(str(self.product), "Perfect Strangers")


class OrderTotalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pass12345")
        self.genre = Genre.objects.create(
            genre_name=Genre.GenreChoices.POP_DISCO, description="desc"
        )
        self.artist = Artist.objects.create(artist_name="ABBA", country="SE")
        self.product1 = Product.objects.create(
            product_name="Waterloo",
            description="Album",
            price=Decimal("50.00"),
            stock_quantity=100,
            genre=self.genre,
            artist=self.artist,
        )
        self.product2 = Product.objects.create(
            product_name="Arrival",
            description="Album",
            price=Decimal("80.00"),
            stock_quantity=100,
            genre=self.genre,
            artist=self.artist,
        )
        self.order = Order.objects.create(user=self.user)

    def test_order_total_without_coupon(self):
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            price_at_order=self.product1.price,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1,
            price_at_order=self.product2.price,
        )
        # 2*50 + 1*80 = 180.00
        self.assertEqual(self.order.get_total(), Decimal("180.00"))

    def test_order_total_with_active_coupon(self):
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=3,
            price_at_order=self.product1.price,
        )
        coupon = Coupon.objects.create(code="SALE10", discount_percent=10, active=True)
        self.order.coupon = coupon
        self.order.save()
        # 150 - 10% = 135.00
        self.assertEqual(self.order.get_total(), Decimal("135.00"))


class LoggerUtilsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="charlie", password="pass12345")
        self.genre = Genre.objects.create(
            genre_name=Genre.GenreChoices.CLASSICAL, description="desc"
        )
        self.artist = Artist.objects.create(artist_name="Mozart", country="AT")
        self.product = Product.objects.create(
            product_name="Requiem",
            description="Album",
            price=Decimal("30.00"),
            stock_quantity=5,
            genre=self.genre,
            artist=self.artist,
        )

    def test_create_log_entry_creates_record(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        create_log_entry(
            action="product_viewed",
            user=self.user,
            description="Просмотр товара",
            ip_address="127.0.0.1",
            user_agent="pytest-agent",
            product=self.product,
        )
        self.assertEqual(LogEntry.objects.count(), 1)
        entry = LogEntry.objects.first()
        self.assertEqual(entry.action, "product_viewed")
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.product, self.product)
        self.assertEqual(entry.ip_address, "127.0.0.1")
        self.assertEqual(entry.user_agent, "pytest-agent")
