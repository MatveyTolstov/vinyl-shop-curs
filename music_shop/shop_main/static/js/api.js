// Общие функции для работы с API
const API_BASE_URL = '/api/v1';

// Глобальная корзина
let cart = {};

// Получение CSRF токена
function getCsrfToken() {
	// Сначала пробуем получить из hidden input
	const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
	if (csrfInput) {
		return csrfInput.value;
	}

	// Если не найден, получаем из cookies
	const name = 'csrftoken';
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(';').shift();
	return '';
}

// Инициализация корзины из cookies
function loadCartFromCookies() {
	try {
		const cartData = document.cookie
			.split('; ')
			.find(row => row.startsWith('cart='));
		if (cartData) {
			cart = JSON.parse(decodeURIComponent(cartData.split('=')[1]));
		}
	} catch (error) {
		cart = {};
	}
}

// Сохранение корзины в cookies
function saveCartToCookies() {
	document.cookie = `cart=${encodeURIComponent(JSON.stringify(cart))}; path=/`;
}

// Добавление в корзину
function addToCart(productId) {
	const productIdStr = String(productId);
	cart[productIdStr] = (cart[productIdStr] || 0) + 1;
	saveCartToCookies();
	showNotification('Товар добавлен в корзину!');
}

// Показ уведомления
function showNotification(message, type = 'success') {
	const notification = document.createElement('div');
	const bgColor = type === 'success' ? '#28a745' : '#dc3545';
	notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
    `;
	notification.textContent = message;
	document.body.appendChild(notification);

	setTimeout(() => {
		notification.remove();
	}, 3000);
}

// Загрузка жанров
async function loadGenres(containerId = 'genre') {
	try {
		const response = await fetch(`${API_BASE_URL}/genres/`);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const genres = await response.json();

		// Проверяем, что genres - это массив
		if (!Array.isArray(genres)) {
			console.error('API вернул не массив:', genres);
			throw new Error('API вернул неожиданный формат данных');
		}

		const container = document.getElementById(containerId);
		if (container) {
			genres.forEach(genre => {
				const option = document.createElement('option');
				option.value = genre.genre_name;
				option.textContent = genre.genre_name;
				container.appendChild(option);
			});
		}
		return genres;
	} catch (error) {
		console.error('Ошибка загрузки жанров:', error);
		return [];
	}
}

// Загрузка исполнителей
async function loadArtists(containerId = 'artist') {
	try {
		const response = await fetch(`${API_BASE_URL}/artists/`);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const artists = await response.json();

		// Проверяем, что artists - это массив
		if (!Array.isArray(artists)) {
			console.error('API вернул не массив:', artists);
			throw new Error('API вернул неожиданный формат данных');
		}

		const container = document.getElementById(containerId);
		if (container) {
			artists.forEach(artist => {
				const option = document.createElement('option');
				option.value = artist.id;
				option.textContent = artist.artist_name;
				container.appendChild(option);
			});
		}
		return artists;
	} catch (error) {
		console.error('Ошибка загрузки исполнителей:', error);
		return [];
	}
}

// Загрузка товаров
async function loadProducts(filters = {}) {
	try {
		const params = new URLSearchParams();
		Object.keys(filters).forEach(key => {
			if (filters[key]) {
				params.append(key, filters[key]);
			}
		});

		const url = `${API_BASE_URL}/products/catalog/${
			params.toString() ? '?' + params.toString() : ''
		}`;
		const response = await fetch(url);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const products = await response.json();

		// Проверяем, что products - это массив
		if (!Array.isArray(products)) {
			console.error('API вернул не массив:', products);
			throw new Error('API вернул неожиданный формат данных');
		}

		return products;
	} catch (error) {
		console.error('Ошибка загрузки товаров:', error);
		return [];
	}
}

// Показ спиннера загрузки
function showSpinner(containerId) {
	const container = document.getElementById(containerId);
	if (container) {
		container.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        `;
	}
}

// Показ ошибки
function showError(containerId, message = 'Произошла ошибка') {
	const container = document.getElementById(containerId);
	if (container) {
		container.innerHTML = `
            <div class="alert alert-danger">${message}</div>
        `;
	}
}
