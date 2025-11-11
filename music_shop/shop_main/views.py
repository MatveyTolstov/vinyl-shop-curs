from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)
import sys

from django.http import HttpResponse
from io import BytesIO

import reportlab
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.units import mm
from django.db.models import Sum

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.models import User, Group
from .forms import (
    SignUpForm,
    LoginForm,
    ReviewForm,
    CheckoutAddressForm,
    ApplyCouponForm,
    ArtistForm,
    ProductForm,
    OrderForm,
    OrderItemForm,
    AdminReviewForm,
    ShippingAddressForm,
    CouponForm,
)
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
import json
from django.utils import timezone
from .models import (
    Genre,
    Artist,
    Product,
    OrderItem,
    Order,
    Review,
    ShippingAddress,
    Coupon,
    LogEntry,
)


class GenreList(TemplateView):
    template_name = "main.html"


class ProductList(TemplateView):
    template_name = "catalog.html"


class ArtistList(ListView):
    model = Artist
    context_object_name = "artists"


class UserDetail(ListView):
    model = User
    context_object_name = "user"
    template_name = "login.html"


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("account")


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "signup.html"
    success_url = reverse_lazy("account")

    def form_valid(self, form):
        response = super().form_valid(form)
        created_user = self.object
        user_group, _ = Group.objects.get_or_create(name="User")
        created_user.groups.add(user_group)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
        return response


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = "account.html"
    login_url = reverse_lazy("login")
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("main")


class ProductDetailView(TemplateView):
    template_name = "product_detail.html"

    def get(self, request, *args, **kwargs):
        # Логируем просмотр товара
        from .logger_utils import create_log_entry
        product_id = kwargs.get('pk')
        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0]
                else:
                    ip_address = request.META.get('REMOTE_ADDR')
                user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
                
                create_log_entry(
                    action='product_viewed',
                    user=request.user if request.user.is_authenticated else None,
                    description=f"Просмотр товара '{product.product_name}'",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    product=product,
                )
            except Product.DoesNotExist:
                pass
        
        return super().get(request, *args, **kwargs)


class CartView(TemplateView):
    template_name = "cart.html"


class FavoritesView(TemplateView):
    template_name = "favorites.html"


class AdminOverviewView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "overview.html"
    login_url = reverse_lazy("login")

    def test_func(self) -> bool:
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_key = self.kwargs.get("model")
        models_map = {
            "genre": Genre,
            "artist": Artist,
            "product": Product,
            "order": Order,
            "orderitem": OrderItem,
            "review": Review,
            "user": User,
        }
        model = models_map.get(model_key)
        if not model:
            raise Http404()
        context["model_name"] = model.__name__
        context["records"] = model.objects.all()[:100]
        context["admin_add_url"] = reverse_lazy(
            "admin:%s_%s_add" % (model._meta.app_label, model._meta.model_name)
        )
        context["admin_changelist_url"] = reverse_lazy(
            "admin:%s_%s_changelist" % (model._meta.app_label, model._meta.model_name)
        )
        context["admin_change_url_name"] = "admin:%s_%s_change" % (
            model._meta.app_label,
            model._meta.model_name,
        )
        return context


class GenreListView(PermissionRequiredMixin, ListView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Genre
    template_name = "genre/list.html"
    context_object_name = "records"


class GenreDetailView(PermissionRequiredMixin, DetailView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Genre
    template_name = "genre/detail.html"
    context_object_name = "object"


class GenreCreateView(PermissionRequiredMixin, CreateView):
    model = Genre
    template_name = "genre/form.html"
    fields = ["genre_name", "description"]
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class GenreUpdateView(PermissionRequiredMixin, UpdateView):
    model = Genre
    template_name = "genre/form.html"
    fields = ["genre_name", "description"]
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class GenreDeleteView(PermissionRequiredMixin, DeleteView):
    model = Genre
    template_name = "genre/confirm_delete.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class ArtistListView(PermissionRequiredMixin, ListView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Artist
    template_name = "artist/list.html"
    context_object_name = "records"


class ArtistDetailView(PermissionRequiredMixin, DetailView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Artist
    template_name = "artist/detail.html"
    context_object_name = "object"


class ArtistCreateView(PermissionRequiredMixin, CreateView):
    model = Artist
    form_class = ArtistForm
    template_name = "artist/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class ArtistUpdateView(PermissionRequiredMixin, UpdateView):
    model = Artist
    form_class = ArtistForm
    template_name = "artist/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class ArtistDeleteView(PermissionRequiredMixin, DeleteView):
    model = Artist
    template_name = "artist/confirm_delete.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


# Product Views
class ProductListView(PermissionRequiredMixin, ListView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Product
    template_name = "product/list.html"
    context_object_name = "records"


class ProductDetailCrudView(PermissionRequiredMixin, DetailView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Product
    template_name = "product/detail.html"
    context_object_name = "object"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "product/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "product/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = "product/confirm_delete.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class OrderListView(PermissionRequiredMixin, ListView):
    model = Order
    template_name = "order/list.html"
    context_object_name = "records"

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related(
                "user", "shipping_address", "coupon"
            ).all()
        return Order.objects.filter(user=self.request.user).select_related(
            "shipping_address", "coupon"
        )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    model = Order
    template_name = "order/detail.html"

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    context_object_name = "object"


class OrderCreateView(PermissionRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "order/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "order/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Сохраняем старый статус для логирования
        obj._old_status = obj.status
        return obj
    
    def form_valid(self, form):
        order = form.instance
        old_status = getattr(order, '_old_status', None)
        
        response = super().form_valid(form)
        
        # Логируем изменение статуса
        if old_status and old_status != order.status:
            from .logger_utils import create_log_entry
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = self.request.META.get('REMOTE_ADDR')
            user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:255]
            
            create_log_entry(
                action='order_updated',
                user=self.request.user,
                description=f"Статус заказа #{order.id} изменен с '{old_status}' на '{order.status}'",
                ip_address=ip_address,
                user_agent=user_agent,
                order=order,
            )
        
        return response


class OrderDeleteView(PermissionRequiredMixin, DeleteView):
    model = Order
    template_name = "order/confirm_delete.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class OrderItemListView(PermissionRequiredMixin, ListView):
    permission_required = "shop_main.view_orderitem"
    model = OrderItem
    template_name = "orderitem/list.html"
    context_object_name = "records"


class OrderItemDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shop_main.view_orderitem"
    model = OrderItem
    template_name = "orderitem/detail.html"
    context_object_name = "object"


class OrderItemCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shop_main.add_orderitem"
    model = OrderItem
    form_class = OrderItemForm
    template_name = "orderitem/form.html"
    success_url = reverse_lazy("db-index")


class OrderItemUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "shop_main.change_orderitem"
    model = OrderItem
    form_class = OrderItemForm
    template_name = "orderitem/form.html"
    success_url = reverse_lazy("db-index")


class OrderItemDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "shop_main.delete_orderitem"
    model = OrderItem
    template_name = "orderitem/confirm_delete.html"
    success_url = reverse_lazy("db-index")


class ReviewListView(PermissionRequiredMixin, ListView):
    permission_required = "shop_main.view_review"
    model = Review
    template_name = "review/list.html"
    context_object_name = "records"


class ReviewDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shop_main.view_review"
    model = Review
    template_name = "review/detail.html"
    context_object_name = "object"


class ReviewCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shop_main.add_review"
    model = Review
    form_class = AdminReviewForm
    template_name = "review/form.html"
    success_url = reverse_lazy("db-index")


class ReviewUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "shop_main.change_review"
    model = Review
    form_class = AdminReviewForm
    template_name = "review/form.html"
    success_url = reverse_lazy("db-index")


class ReviewDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "shop_main.delete_review"
    model = Review
    template_name = "review/confirm_delete.html"
    success_url = reverse_lazy("db-index")


class ShippingAddressListView(PermissionRequiredMixin, ListView):
    permission_required = "shop_main.view_shippingaddress"
    model = ShippingAddress
    template_name = "shippingaddress/list.html"
    context_object_name = "records"

    def get_queryset(self):
        if self.request.user.is_staff:
            return ShippingAddress.objects.select_related("user").all()
        return ShippingAddress.objects.filter(user=self.request.user)


class ShippingAddressDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shop_main.view_shippingaddress"
    model = ShippingAddress
    template_name = "shippingaddress/detail.html"
    context_object_name = "object"


class ShippingAddressCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shop_main.add_shippingaddress"
    model = ShippingAddress
    form_class = ShippingAddressForm
    template_name = "shippingaddress/form.html"
    success_url = reverse_lazy("db-index")


class ShippingAddressUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "shop_main.change_shippingaddress"
    model = ShippingAddress
    form_class = ShippingAddressForm
    template_name = "shippingaddress/form.html"
    success_url = reverse_lazy("db-index")


class ShippingAddressDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "shop_main.delete_shippingaddress"
    model = ShippingAddress
    template_name = "shippingaddress/confirm_delete.html"
    success_url = reverse_lazy("db-index")


class CouponListView(PermissionRequiredMixin, ListView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Coupon
    template_name = "coupon/list.html"
    context_object_name = "records"


class CouponDetailView(PermissionRequiredMixin, DetailView):
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

    model = Coupon
    template_name = "coupon/detail.html"
    context_object_name = "object"


class CouponCreateView(PermissionRequiredMixin, CreateView):
    model = Coupon
    form_class = CouponForm
    template_name = "coupon/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class CouponUpdateView(PermissionRequiredMixin, UpdateView):
    model = Coupon
    form_class = CouponForm
    template_name = "coupon/form.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class CouponDeleteView(PermissionRequiredMixin, DeleteView):
    model = Coupon
    template_name = "coupon/confirm_delete.html"
    success_url = reverse_lazy("db-index")

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class DatabaseOverviewView(PermissionRequiredMixin, TemplateView):
    template_name = "db/index.html"
    login_url = reverse_lazy("login")

    def has_permission(self):
        if self.request.user.is_authenticated:
            is_staff = self.request.user.is_staff or self.request.user.is_superuser
            is_manager = self.request.user.groups.filter(name="Manager").exists()
            return is_staff or is_manager
        return False

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        is_manager = self.request.user.groups.filter(name="Manager").exists()
        is_staff = self.request.user.is_staff or self.request.user.is_superuser
        ctx["is_manager"] = is_manager
        ctx["is_staff"] = is_staff

        ctx["genres"] = Genre.objects.all()
        ctx["artists"] = Artist.objects.all()
        ctx["products"] = Product.objects.select_related("genre", "artist").all()

        ctx["show_all"] = is_staff or self.request.user.is_superuser
        ctx["show_orders"] = ctx["show_all"] or is_manager

        if ctx["show_all"]:
            orders = (
                Order.objects.select_related("user", "shipping_address", "coupon")
                .prefetch_related("orderitem_set")
                .all()
            )
            ctx["orders"] = orders
            ctx["order_items"] = OrderItem.objects.select_related(
                "order", "product"
            ).all()
            ctx["reviews"] = Review.objects.select_related("user", "product").all()
            ctx["shipping_addresses"] = ShippingAddress.objects.select_related(
                "user"
            ).all()
            ctx["coupons"] = Coupon.objects.all()
            ctx["users"] = User.objects.all()
            ctx["groups"] = Group.objects.all()
        elif is_manager:
            orders = (
                Order.objects.select_related("user", "shipping_address", "coupon")
                .prefetch_related("orderitem_set")
                .all()
            )
            ctx["orders"] = orders
            ctx["order_items"] = OrderItem.objects.select_related(
                "order", "product"
            ).all()
            ctx["reviews"] = []  
            ctx["shipping_addresses"] = ShippingAddress.objects.select_related(
                "user"
            ).all()
            ctx["coupons"] = Coupon.objects.all()  
            ctx["users"] = []
            ctx["groups"] = []
        else:
            ctx["orders"] = []
            ctx["order_items"] = []
            ctx["reviews"] = []
            ctx["shipping_addresses"] = []
            ctx["coupons"] = []
            ctx["users"] = []
            ctx["groups"] = []

        ctx["tables"] = [
            {"name": "Жанры", "count": Genre.objects.count(), "url": "genre-list"},
            {
                "name": "Исполнители",
                "count": Artist.objects.count(),
                "url": "artist-list",
            },
            {"name": "Товары", "count": Product.objects.count(), "url": "product-list"},
        ]
        if ctx["show_orders"]:
            ctx["tables"].append(
                {"name": "Заказы", "count": Order.objects.count(), "url": "order-list"}
            )
            if ctx["show_all"]:
                ctx["tables"].append(
                    {
                        "name": "Отзывы",
                        "count": Review.objects.count(),
                        "url": "review-list",
                    }
                )
                ctx["tables"].append(
                    {
                        "name": "Позиции заказа",
                        "count": OrderItem.objects.count(),
                        "url": "orderitem-list",
                    }
                )
                ctx["tables"].append(
                    {
                        "name": "Адреса доставки",
                        "count": ShippingAddress.objects.count(),
                        "url": "shippingaddress-list",
                    }
                )
            ctx["tables"].append(
                {
                    "name": "Купоны",
                    "count": Coupon.objects.count(),
                    "url": "coupon-list",
                }
            )
        if ctx["show_all"]:
            ctx["tables"].extend(
                [
                    {"name": "Пользователи", "count": User.objects.count(), "url": "#"},
                    {
                        "name": "Роли (Группы)",
                        "count": Group.objects.count(),
                        "url": "#",
                    },
                ]
            )

        from django.db.models import Sum, Count

        order_items = OrderItem.objects.all()
        total_revenue = sum(item.price_at_order * item.quantity for item in order_items)
        ctx["total_revenue"] = float(total_revenue)
        ctx["total_orders"] = Order.objects.count()
        ctx["total_products"] = Product.objects.count()
        ctx["total_customers"] = User.objects.count()

        popular_products = (
            OrderItem.objects.values("product__product_name", "product__id")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:5]
        )
        ctx["popular_products"] = list(popular_products)

        genre_stats = []
        for genre in Genre.objects.all():
            product_count = Product.objects.filter(genre=genre).count()
            if product_count > 0:
                genre_stats.append(
                    {"name": genre.get_genre_name_display(), "count": product_count}
                )
        ctx["genre_stats"] = genre_stats

        artist_stats = []
        for artist in Artist.objects.all():
            product_count = Product.objects.filter(artist=artist).count()
            if product_count > 0:
                artist_stats.append(
                    {"name": artist.artist_name, "count": product_count}
                )
        ctx["artist_stats"] = artist_stats[:10]  # Топ 10

        return ctx


class GeneratePDFReportView(PermissionRequiredMixin, View):
    """View для генерации PDF отчета с общей выручкой"""

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )

   
    def get(self, request, *args, **kwargs):
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1e293b"),
                spaceAfter=30,
                fontName="Times-Roman"
            )

            elements.append(Paragraph("Report", title_style))
            elements.append(Spacer(1, 20))

            order_items = OrderItem.objects.all()
            total_revenue = sum(
                item.price_at_order * item.quantity for item in order_items
            )

            total_orders = Order.objects.count()
            total_products = Product.objects.count()
            total_customers = User.objects.count()

            popular_products = (
                OrderItem.objects.values("product__product_name")
                .annotate(total_sold=Sum("quantity"))
                .order_by("-total_sold")[:5]
            )

            data = [
                ["Metric", "Value"],
                ["Total revenue", f"{total_revenue:,.0f}"],
                ["Total orders", f"{total_orders}"],
                ["Total products", f"{total_products}"],
                ["Total customers", f"{total_customers}"],
            ]

            table = Table(data, colWidths=[120 * mm, 70 * mm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#64748b")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Times-Roman"),
                        ("FONTSIZE", (0, 0), (-1, 0), 14),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f8fafc")],
                        ),
                    ]
                )
            )

            elements.append(table)
            elements.append(Spacer(1, 30))

            if popular_products:
                elements.append(Paragraph("Popular products", styles["Heading2"]))
                elements.append(Spacer(1, 10))

                popular_data = [["Product", "Sold (pcs)"]]
                for product in popular_products:
                    popular_data.append(
                        [product["product__product_name"], f"{product['total_sold']}"]
                    )

                popular_table = Table(popular_data, colWidths=[120 * mm, 70 * mm])
                popular_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#64748b")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Times-Roman"),
                            ("FONTSIZE", (0, 0), (-1, 0), 14),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [colors.white, colors.HexColor("#f8fafc")],
                            ),
                        ]
                    )
                )

                elements.append(popular_table)

            doc.build(elements)

            pdf = buffer.getvalue()
            buffer.close()

            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="report_revenue.pdf"'

            return response

        except ImportError as e:
            return JsonResponse(
                {
                    "error": "reportlab is not installed",
                    "message": f"Import error: {str(e)}",
                    "data": {
                        "total_revenue": total_revenue,
                        "total_orders": total_orders,
                        "total_products": total_products,
                        "total_customers": total_customers,
                    },
                }
            )
        except Exception as e:
            # Handle all other errors
            return JsonResponse(
                {
                    "error": "PDF generation error",
                    "message": f"Error: {str(e)}",
                    "data": {
                        "total_revenue": total_revenue,
                        "total_orders": total_orders,
                        "total_products": total_products,
                        "total_customers": total_customers,
                    },
                }
            )


class LogEntryListView(PermissionRequiredMixin, ListView):
    """View для отображения списка логов"""
    
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )
    
    model = LogEntry
    template_name = "log/list.html"
    context_object_name = "logs"
    paginate_by = 50
    
    def get_queryset(self):
        queryset = LogEntry.objects.select_related(
            "user", "order", "product"
        ).all()
        
        # Фильтрация по действию
        action_filter = self.request.GET.get("action")
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        # Фильтрация по пользователю
        user_filter = self.request.GET.get("user")
        if user_filter:
            queryset = queryset.filter(user_id=user_filter)
        
        # Поиск по описанию
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(description__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action_choices"] = LogEntry.ACTION_CHOICES
        context["users"] = User.objects.filter(
            log_entries__isnull=False
        ).distinct()
        return context