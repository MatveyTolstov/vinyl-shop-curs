// Функции для корзины
document.addEventListener('DOMContentLoaded', function () {
	loadCartFromCookies();

	// Debug: проверяем состояние корзины
	console.log('Загружена корзина из cookies:', cart);
	console.log(
		'Типы ключей корзины:',
		Object.keys(cart).map(k => typeof k)
	);
	console.log(
		'Значения корзины:',
		Object.keys(cart).map(k => typeof cart[k])
	);

	loadCartItems();
});

// Загрузка товаров корзины
async function loadCartItems() {
	const productIds = Object.keys(cart);
	if (productIds.length === 0) {
		showEmptyCart();
		return;
	}

	showSpinner('cart-content');

	try {
		// Создаем копию корзины для работы
		const cartCopy = { ...cart };

		// Загружаем каждый товар отдельно и удаляем несуществующие из корзины
		const productPromises = productIds.map(async id => {
			try {
				const response = await fetch(`${API_BASE_URL}/products/${id}/`);
				if (!response.ok) {
					console.warn(`Товар ${id} не найден, удаляем из корзины`);
					delete cartCopy[id];
					return null;
				}
				const product = await response.json();
				return product;
			} catch (err) {
				console.error(`Ошибка загрузки товара ${id}:`, err);
				delete cartCopy[id];
				return null;
			}
		});

		const products = await Promise.all(productPromises);
		// Фильтруем null значения
		const validProducts = products.filter(p => p !== null);

		// Если не осталось товаров, показываем пустую корзину
		if (validProducts.length === 0) {
			cart = {};
			saveCartToCookies();
			showEmptyCart();
			return;
		}

		// Обновляем корзину только если были изменения
		if (Object.keys(cartCopy).length !== Object.keys(cart).length) {
			cart = cartCopy;
			saveCartToCookies();
		}

		console.log('Загруженные товары:', validProducts);
		console.log('Корзина после загрузки:', cart);
		displayCartItems(validProducts);
	} catch (error) {
		console.error('Ошибка загрузки товаров корзины:', error);
		showError('cart-content', 'Ошибка загрузки товаров корзины');
	}
}

// Отображение товаров корзины
function displayCartItems(products) {
	const container = document.getElementById('cart-content');
	if (!container) return;

	let total = 0;
	let cartHtml = `
        <table style="width: 100%; border-collapse: collapse">
            <thead>
                <tr>
                    <th style="text-align: left; padding: 8px 0">Товар</th>
                    <th style="text-align: left; padding: 8px 0">Цена</th>
                    <th style="text-align: left; padding: 8px 0">Кол-во</th>
                    <th style="text-align: left; padding: 8px 0">Сумма</th>
                    <th></th>
                </tr>
            </thead>
            <tbody id="cart-items">
    `;
	console.log('Товары для отображения:', products);
	console.log('Корзина:', cart);
	console.log('Все ключи корзины:', Object.keys(cart));

	products.forEach(product => {
		// Проверяем, что товар валиден
		if (!product || !product.id || !product.product_name) {
			console.warn('Пропускаем невалидный товар:', product);
			return;
		}

		const productIdStr = String(product.id);
		console.log(`Обрабатываем товар ${product.id}`);
		console.log('Ищем в корзине по строке:', cart[productIdStr]);
		console.log('Ищем в корзине по числу:', cart[product.id]);

		// Пробуем найти по строке или по числу
		const quantity = cart[productIdStr] || cart[product.id];
		console.log('Найдено количество:', quantity);

		if (!quantity || quantity === 0) {
			console.warn('Нет количества для товара:', product.id);
			return;
		}

		const subtotal = parseFloat(product.price) * quantity;
		total += subtotal;

		cartHtml += `
            <tr style="border-top: 1px solid #e5e7eb">
                <td style="padding: 12px 0">${product.product_name}</td>
                <td style="padding: 12px 0">${product.price} ₽</td>
                <td style="padding: 12px 0">
                    <button class="add-to-cart-btn" onclick="updateCartQuantity(${
											product.id
										}, -1)">-</button>
                    <span style="display: inline-block; width: 24px; text-align: center">${quantity}</span>
                    <button class="add-to-cart-btn" onclick="updateCartQuantity(${
											product.id
										}, 1)">+</button>
                </td>
                <td style="padding: 12px 0">${subtotal.toFixed(2)} ₽</td>
                <td style="padding: 12px 0">
                    <button class="add-to-cart-btn" onclick="removeFromCart(${
											product.id
										})">Удалить</button>
                </td>
            </tr>
        `;
	});

	// Проверяем, что есть хотя бы один товар
	if (total === 0 && products.length > 0) {
		cartHtml =
			'<p class="muted">Не удалось загрузить информацию о товарах. Пожалуйста, обновите страницу.</p>';
		container.innerHTML = cartHtml;
		return;
	}

	if (total === 0) {
		cartHtml = '<p class="muted">Ваша корзина пуста.</p>';
		container.innerHTML = cartHtml;
		return;
	}

	cartHtml += `
            </tbody>
        </table>
        <div style="text-align: right; margin-top: 16px">
            <p class="product-price">Итого: <span id="cart-total">${total.toFixed(
							2
						)}</span> ₽</p>
            <form id="checkout-form" style="display: block; text-align: left; margin-top: 12px">
                <div class="card" style="padding: 12px; margin-bottom: 12px">
                    <h3 style="margin: 0 0 8px 0">Адрес доставки</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px">
                        <div>
                            <label for="full_name">ФИО</label>
                            <input type="text" id="full_name" name="full_name" required>
                        </div>
                        <div>
                            <label for="phone">Телефон</label>
                            <input type="tel" id="phone" name="phone" required>
                        </div>
                        <div>
                            <label for="city">Город</label>
                            <input type="text" id="city" name="city" required>
                        </div>
                        <div>
                            <label for="address_line">Адрес</label>
                            <input type="text" id="address_line" name="address_line" required>
                        </div>
                        <div>
                            <label for="postal_code">Почтовый индекс</label>
                            <input type="text" id="postal_code" name="postal_code" required>
                        </div>
                    </div>
                </div>

                <div class="card" style="padding: 12px; margin-bottom: 12px">
                    <h3 style="margin: 0 0 8px 0">Промокод</h3>
                    <div style="display: flex; gap: 8px; align-items: center">
                        <input type="text" id="coupon_code" name="coupon_code" placeholder="Введите код купона">
                    </div>
                </div>

                <button type="button" class="add-to-cart-btn" onclick="checkout()">
                    Оформить заказ
                </button>
            </form>
        </div>
    `;

	container.innerHTML = cartHtml;
}

// Обновление количества товара в корзине
function updateCartQuantity(productId, change) {
	const productIdStr = String(productId);
	const currentQty = cart[productIdStr] || 0;
	const newQty = currentQty + change;

	if (newQty <= 0) {
		delete cart[productIdStr];
	} else {
		cart[productIdStr] = newQty;
	}

	saveCartToCookies();
	loadCartItems();
}

// Удаление товара из корзины
function removeFromCart(productId) {
	const productIdStr = String(productId);
	delete cart[productIdStr];
	saveCartToCookies();
	loadCartItems();
}

// Показ пустой корзины
function showEmptyCart() {
	const container = document.getElementById('cart-content');
	if (container) {
		container.innerHTML = '<p class="muted">Ваша корзина пуста.</p>';
	}
}

// Оформление заказа
async function checkout() {
	const formData = {
		shipping_address: {
			full_name: document.getElementById('full_name').value,
			phone: document.getElementById('phone').value,
			city: document.getElementById('city').value,
			address_line: document.getElementById('address_line').value,
			postal_code: document.getElementById('postal_code').value,
		},
		coupon_code: document.getElementById('coupon_code').value,
	};

	try {
		// Получаем CSRF токен
		const csrfToken = getCsrfToken();

		// Debug: проверяем корзину перед отправкой
		console.log('Корзина перед отправкой:', cart);
		console.log('Cookies:', document.cookie);

		const response = await fetch(`${API_BASE_URL}/cart/checkout/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': csrfToken,
			},
			credentials: 'include', // Важно для передачи cookies с sessionid
			body: JSON.stringify(formData),
		});

		if (response.ok) {
			cart = {};
			saveCartToCookies();
			showNotification('Заказ успешно оформлен!');

			// Перенаправляем на главную страницу
			setTimeout(() => {
				window.location.href = '/';
			}, 2000);
		} else {
			const error = await response.json();
			showNotification(
				'Ошибка оформления заказа: ' + (error.error || 'Неизвестная ошибка'),
				'error'
			);
		}
	} catch (error) {
		console.error('Ошибка оформления заказа:', error);
		showNotification('Ошибка оформления заказа', 'error');
	}
}
