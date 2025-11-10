# Музыкальный магазин - API

Этот проект представляет собой музыкальный магазин виниловых пластинок с полноценным REST API на Django REST Framework.

## Возможности

- **Полноценное API** для всех операций с товарами, заказами, отзывами
- **Публичный каталог** товаров с фильтрацией и поиском
- **Система корзины** с возможностью оформления заказов
- **Система отзывов** для товаров
- **Управление купонами** и скидками
- **Административная панель** для управления контентом
- **CORS поддержка** для фронтенд приложений

## Установка и запуск

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Выполните миграции:

```bash
python manage.py migrate
```

3. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

4. Запустите сервер:

```bash
python manage.py runserver
```

## API Endpoints

### Базовый URL

```
/api/v1/
```

### Основные endpoints:

#### Товары

- `GET /products/catalog/` - Публичный каталог товаров
- `GET /products/{id}/` - Детали товара
- `POST /products/{id}/add_to_cart/` - Добавить в корзину

#### Корзина

- `GET /cart/get_cart/` - Получить содержимое корзины
- `POST /cart/add_item/` - Добавить товар в корзину
- `POST /cart/checkout/` - Оформить заказ

#### Отзывы

- `GET /reviews/product_reviews/?product_id={id}` - Отзывы товара
- `POST /reviews/create_review/` - Создать отзыв

#### Купоны

- `POST /coupons/validate_coupon/` - Проверить купон

#### Пользователи

- `GET /users/me/` - Информация о текущем пользователе

### Фильтрация каталога

Параметры запроса для `/products/catalog/`:

- `genre` - фильтр по жанру
- `artist` - фильтр по исполнителю (ID)
- `min_price` - минимальная цена
- `max_price` - максимальная цена
- `search` - поиск по названию или исполнителю
- `sort` - сортировка (price, -price, product_name, -product_name, created_at, -created_at)

Пример:

```
GET /api/v1/products/catalog/?genre=rock and metal&min_price=100&sort=-price
```

## Фронтенд

### API Фронтенд

Доступен по адресу `/api-frontend/` - это полнофункциональный фронтенд на JavaScript, который работает с API.

### API Документация

Доступна по адресу `/api-docs/` - подробная документация по всем API endpoints.

### Административная панель

Доступна по адресу `/admin/` - стандартная Django админка для управления данными.

## Структура проекта

```
music_shop/
├── music_shop/          # Основные настройки Django
├── shop_main/           # Главное приложение
│   ├── models.py        # Модели данных
│   ├── serializers.py   # DRF сериализаторы
│   ├── api.py          # API viewsets
│   ├── views.py        # Django views
│   ├── urls.py         # URL маршруты
│   └── templates/      # HTML шаблоны
└── requirements.txt    # Зависимости
```

## Модели данных

- **Genre** - Жанры музыки
- **Artist** - Исполнители
- **Product** - Товары (виниловые пластинки)
- **Order** - Заказы
- **OrderItem** - Позиции заказа
- **Review** - Отзывы
- **ShippingAddress** - Адреса доставки
- **Coupon** - Купоны

## Аутентификация

API поддерживает:

- Session Authentication (для веб-интерфейса)
- Basic Authentication (для API клиентов)

Большинство endpoints требуют аутентификации, кроме публичного каталога товаров.

## CORS

Настроена поддержка CORS для фронтенд приложений. В режиме отладки разрешены все origins.

## Примеры использования

### Получить каталог товаров

```bash
curl -X GET "http://localhost:8000/api/v1/products/catalog/?genre=rock and metal"
```

### Добавить товар в корзину

```bash
curl -X POST "http://localhost:8000/api/v1/products/1/add_to_cart/" \
  -H "Content-Type: application/json"
```

### Создать отзыв

```bash
curl -X POST "http://localhost:8000/api/v1/reviews/create_review/" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "rating": 5,
    "text": "Отличный альбом!"
  }'
```

## Разработка

Для разработки рекомендуется:

1. Использовать виртуальное окружение
2. Настроить IDE для работы с Django
3. Использовать Django Debug Toolbar для отладки
4. Писать тесты для новых функций

## Лицензия

Этот проект создан в образовательных целях.



