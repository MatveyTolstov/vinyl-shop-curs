from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    Review,
    ShippingAddress,
    Artist,
    Genre,
    Product,
    Order,
    OrderItem,
    Coupon,
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text="Обязательное поле. Введите действующий email.",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите имя пользователя",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите пароль"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Подтвердите пароль"}
        )


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите имя пользователя",
                "autocomplete": "username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль",
                "autocomplete": "current-password",
            }
        )
    )


from django import forms
from .models import *


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ("genre_name", "description")
        widgets = {
            "genre_name": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Описание жанра...",
                }
            ),
        }


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ("artist_name", "country")
        widgets = {
            "artist_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название исполнителя",
                }
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите страну"}
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "product_name",
            "description",
            "price",
            "stock_quantity",
            "picture",
            "genre",
            "artist",
        )
        widgets = {
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название альбома или пластинки",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Описание продукта...",
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "stock_quantity": forms.NumberInput(
                attrs={"class": "form-control", "min": "0"}
            ),
            "picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "genre": forms.Select(attrs={"class": "form-select"}),
            "artist": forms.Select(attrs={"class": "form-select"}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("user", "status", "shipping_address", "coupon")
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "shipping_address": forms.Select(attrs={"class": "form-select"}),
            "coupon": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['shipping_address'].required = False
        self.fields['coupon'].required = False


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ("order", "product", "quantity")
        widgets = {
            "order": forms.Select(attrs={"class": "form-select"}),
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "value": "1"}
            ),
        }


class AdminReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("user", "product", "rating", "text")
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "product": forms.Select(attrs={"class": "form-select"}),
            "rating": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.5", "min": "0", "max": "5"}
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Текст отзыва...",
                }
            ),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {
            "rating": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.5", "min": "0", "max": "5"}
            ),
            "text": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Поделитесь впечатлениями..."}
            ),
        }


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ("user", "full_name", "phone", "city", "address_line", "postal_code")
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address_line": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
        }


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ("code", "discount_percent", "active", "valid_from", "valid_to")
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "discount_percent": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "max": "100"}
            ),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "valid_from": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "valid_to": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }


class CheckoutAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ("full_name", "phone", "city", "address_line", "postal_code")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address_line": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
        }


class ApplyCouponForm(forms.Form):
    code = forms.CharField(
        required=False,
        label="Промокод",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Введите промокод"}
        ),
    )
