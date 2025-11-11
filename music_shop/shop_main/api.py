from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
import json

from .models import (
    Genre,
    Artist,
    Product,
    Order,
    OrderItem,
    Review,
    ShippingAddress,
    Coupon,
    Favorite,
)
from .serializers import (
    GenreSerializer,
    ArtistSerializer,
    ProductSerializer,
    OrderSerializer,
    OrderItemSerializer,
    ReviewSerializer,
    ShippingAddressSerializer,
    CouponSerializer,
    UserSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    ShippingAddressInputSerializer,
    CheckoutSerializer,
    ApplyCouponSerializer,
    ProductFilterSerializer,
    FavoriteSerializer,
    FavoriteToggleSerializer,
)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["genre_name"]
    ordering_fields = ["genre_name"]
    ordering = ["genre_name"]


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["artist_name"]
    ordering_fields = ["artist_name"]
    ordering = ["artist_name"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("genre", "artist").all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        """
        Разрешаем просмотр для всех, но изменение/удаление только для админов
        """
        if self.action in ['list', 'retrieve', 'catalog', 'add_to_cart']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["product_name", "artist__artist_name"]
    ordering_fields = ["product_name", "price", "created_at"]
    ordering = ["-created_at"]
    filterset_fields = ["genre", "artist"]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def catalog(self, request):
        """Публичный каталог товаров для пользователей"""
        queryset = self.get_queryset()
        

        genre_filter = request.GET.get("genre")
        if genre_filter:
            queryset = queryset.filter(genre__genre_name=genre_filter)

        artist_filter = request.GET.get("artist")
        if artist_filter:
            queryset = queryset.filter(artist__id=artist_filter)

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        search = request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(product_name__icontains=search)
                | Q(artist__artist_name__icontains=search)
            )

        sort_by = request.GET.get("sort", "created_at")
        if sort_by in ["price", "-price", "product_name", "-product_name", "created_at", "-created_at"]:
            queryset = queryset.order_by(sort_by)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_to_cart(self, request, pk=None):
        """Добавить товар в корзину"""
        product = self.get_object()
        if product.stock_quantity <= 0:
            return Response(
                {"error": "Товар закончился"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        


        return Response({"message": "Товар добавлен в корзину"})


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user", "shipping_address", "coupon").all()
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        """
        Разрешаем просмотр заказов для авторизованных пользователей
        """
        if self.action in ['list', 'retrieve', 'my_orders']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["status"]
    ordering_fields = ["date_order", "status"]
    ordering = ["-date_order"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_orders(self, request):
        """Получить заказы текущего пользователя"""
        from django.db.models import Prefetch
        orders = Order.objects.filter(user=request.user).select_related(
            'user', 'shipping_address', 'coupon'
        ).prefetch_related(
            Prefetch('orderitem_set', queryset=OrderItem.objects.select_related('product'))
        ).order_by("-date_order")
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related("order", "product").all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ["product__product_name"]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "product").all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def product_reviews(self, request):
        """Получить отзывы для конкретного товара"""
        product_id = request.GET.get("product_id")
        if not product_id:
            return Response(
                {"error": "product_id обязателен"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = Review.objects.filter(product_id=product_id).select_related("user").order_by("-created_at")
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_review(self, request):
        """Создать отзыв"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            if Review.objects.filter(user=request.user, product_id=request.data.get('product')).exists():
                return Response(
                    {"error": "Вы уже оставили отзыв на этот товар"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.select_related("user").all()
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ["city"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_addresses(self, request):
        """Получить адреса текущего пользователя"""
        addresses = ShippingAddress.objects.filter(user=request.user).order_by("-created_at")
        serializer = self.get_serializer(addresses, many=True)
        return Response(serializer.data)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ["code"]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_coupon(self, request):
        """Проверить валидность купона"""
        code = request.data.get('code', '').strip()
        if not code:
            return Response(
                {"error": "Код купона обязателен"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True)
            now = timezone.now()
            
            if ((coupon.valid_from and coupon.valid_from > now) or 
                (coupon.valid_to and coupon.valid_to < now)):
                return Response(
                    {"error": "Купон недействителен"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response(
                {"error": "Купон не найден"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class CartViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        """
        Для тестирования разрешаем все операции без авторизации
        В продакшене checkout должен требовать авторизацию
        """
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def get_cart(self, request):
        """Получить содержимое корзины"""
        try:
            cart = json.loads(request.COOKIES.get("cart", "{}"))
        except json.JSONDecodeError:
            cart = {}
        
        product_ids = [int(pid) for pid in cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        items = []
        total = 0.0
        
        for pid, qty in cart.items():
            pid_int = int(pid)
            product = products.get(pid_int)
            if not product:
                continue
            price = float(product.price)
            subtotal = price * qty
            total += subtotal
            items.append({
                "id": pid_int,
                "product": ProductSerializer(product).data,
                "quantity": qty,
                "price": price,
                "subtotal": subtotal,
            })
        
        return Response({"items": items, "total": total})

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Добавить товар в корзину"""
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            try:
                product = Product.objects.get(id=product_id)
                if product.stock_quantity <= 0:
                    return Response(
                        {"error": "Товар закончился"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                

                return Response({"message": "Товар добавлен в корзину"})
            except Product.DoesNotExist:
                return Response(
                    {"error": "Товар не найден"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Оформить заказ"""

        import pprint
        import urllib.parse
        print("Все cookies:", pprint.pformat(request.COOKIES))
        
        try:

            cart_cookie = request.COOKIES.get("cart", "{}")
            cart_decoded = urllib.parse.unquote(cart_cookie)
            cart = json.loads(cart_decoded)
            print("Корзина из cookies (raw):", cart_cookie)
            print("Корзина из cookies (decoded):", cart_decoded)
            print("Корзина из cookies (parsed):", cart)
        except json.JSONDecodeError as e:
            print("Ошибка парсинга cart:", e)
            cart = {}
        
        if not cart:
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        address_data = serializer.validated_data['shipping_address']
        

        if request.user.is_authenticated:

            shipping_address = ShippingAddress.objects.create(
                user=request.user,
                full_name=address_data['full_name'],
                phone=address_data['phone'],
                city=address_data['city'],
                address_line=address_data['address_line'],
                postal_code=address_data['postal_code']
            )
            

            product_ids = [int(pid) for pid in cart.keys()]
            products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
            

            order = Order.objects.create(
                user=request.user,
                status="pending",
                shipping_address=shipping_address
            )
            
            coupon_code = serializer.validated_data.get('coupon_code', '').strip()
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                    now = timezone.now()
                    if ((not coupon.valid_from or coupon.valid_from <= now) and 
                        (not coupon.valid_to or coupon.valid_to >= now)):
                        order.coupon = coupon
                        order.save()
                except Coupon.DoesNotExist:
                    pass
            

            for pid_str, qty in cart.items():
                pid = int(pid_str)
                product = products.get(pid)
                if not product:
                    continue
                if product.stock_quantity < qty:
                    qty = product.stock_quantity
                if qty <= 0:
                    continue
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price_at_order=product.price
                )

                product.stock_quantity -= qty
                product.save()
            
            # Логируем создание заказа ПОСЛЕ создания всех OrderItem'ов
            from .logger_utils import create_log_entry
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            
            # Обновляем заказ из БД, чтобы получить актуальные OrderItem'ы
            order.refresh_from_db()
            total = order.get_total()
            description = f"Создан заказ #{order.id} на сумму {total:.2f} ₽"
            if order.coupon:
                description += f" (применен купон {order.coupon.code})"
            
            create_log_entry(
                action='order_created',
                user=request.user,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                order=order,
            )
            
            return Response({
                "message": "Заказ создан",
                "order_id": order.id
            })
        else:

            return Response({
                "message": "Для оформления заказа необходимо войти в систему"
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Получить информацию о текущем пользователе"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Избранные товары текущего пользователя"""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related("product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def products(self, request):
        """Вернуть список товаров (Product) из избранного"""
        favorites = self.get_queryset()
        products = [fav.product for fav in favorites]
        data = ProductSerializer(products, many=True).data
        return Response(data)

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        """Добавить/удалить товар из избранного по product_id"""
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            fav.delete()
            return Response({"status": "removed"})
        return Response({"status": "added"})

    @action(detail=False, methods=["post"])
    def add(self, request):
        """Добавить конкретный товар по product_id"""
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        Favorite.objects.get_or_create(user=request.user, product=product)
        return Response({"status": "added"})

    @action(detail=False, methods=["post"])
    def remove(self, request):
        """Удалить конкретный товар по product_id"""
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        Favorite.objects.filter(user=request.user, product=product).delete()
        return Response({"status": "removed"})


router = DefaultRouter()
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"artists", ArtistViewSet, basename="artist")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items", OrderItemViewSet, basename="orderitem")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"addresses", ShippingAddressViewSet, basename="shippingaddress")
router.register(r"coupons", CouponViewSet, basename="coupon")
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"users", UserViewSet, basename="user")
router.register(r"favorites", FavoriteViewSet, basename="favorite")
