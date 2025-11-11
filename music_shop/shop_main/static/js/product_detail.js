// Функции для страницы товара
document.addEventListener('DOMContentLoaded', function () {
	loadProduct();
	loadReviews();
});

// Получаем ID товара из URL
function getProductId() {
	const path = window.location.pathname;
	const match = path.match(/\/product\/(\d+)\//);
	return match ? match[1] : null;
}

// Загрузка данных товара
async function loadProduct() {
	const productId = getProductId();
	if (!productId) {
		document.getElementById('product-container').innerHTML =
			'<div class="alert alert-danger">Товар не найден</div>';
		return;
	}

	try {
		const response = await fetch(`${API_BASE_URL}/products/${productId}/`);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const product = await response.json();
		displayProduct(product);

		// Показываем раздел отзывов
		document.getElementById('reviews-container').style.display = 'block';
	} catch (error) {
		console.error('Ошибка загрузки товара:', error);
		document.getElementById('product-container').innerHTML =
			'<div class="alert alert-danger">Ошибка загрузки товара</div>';
	}
}

// Отображение товара
function displayProduct(product) {
	const container = document.getElementById('product-container');

	const html = `
        <div class="product-page">
            <button 
                class="fav-btn" 
                aria-label="Избранное" 
                data-product-id="${product.id}"
                type="button"
                style="position:absolute; right:10px; top:10px; background:#fff; border:1px solid #e5e7eb; border-radius:9999px; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; z-index:2; pointer-events:auto;">
                <span class="heart" style="font-size:16px;">♡</span>
            </button>
            <div>
                ${
									product.picture
										? `<img src="${product.picture}" alt="${product.product_name}" class="product-image" />`
										: '<div class="vinyl-placeholder">🎵</div>'
								}
            </div>
            <div>
                <h1 class="product-title">${product.product_name}</h1>
                <p class="product-meta">
                    Исполнитель: ${product.artist_name} • Жанр: ${
		product.genre_name
	}
                </p>
                <p class="product-desc">${product.description}</p>
                <p class="product-price">Цена: ${product.price} ₽</p>
                <p class="stock-status">
                    ${
											product.stock_quantity > 0
												? `В наличии: ${product.stock_quantity} шт.`
												: 'Нет в наличии'
										}
                </p>
                <button 
                    class="add-to-cart-btn" 
                    onclick="addToCart(${product.id})"
                    ${product.stock_quantity <= 0 ? 'disabled' : ''}
                >
                    Добавить в корзину
                </button>
            </div>
        </div>
    `;

	container.innerHTML = html;

	// Init favorite state
	const favBtn = container.querySelector('.fav-btn');
	const heart = favBtn.querySelector('.heart');
	if (typeof ensureFavoritesLoaded === 'function') {
		ensureFavoritesLoaded().then(() => {
			try {
				if (typeof isFavorite === 'function' && isFavorite(product.id)) {
					heart.textContent = '❤';
					heart.style.color = '#dc2626';
				}
			} catch (e) {}
		}).catch(() => {});
	}
	favBtn.addEventListener('click', async (e) => {
		e.stopPropagation();
		if (typeof toggleFavorite !== 'function') return;
		const result = await toggleFavorite(product.id);
		if (result.status === 'added') {
			heart.textContent = '❤';
			heart.style.color = '#dc2626';
		} else if (result.status === 'removed') {
			heart.textContent = '♡';
			heart.style.color = '';
		}
	});
}

// Загрузка отзывов
async function loadReviews() {
	const productId = getProductId();
	if (!productId) return;

	try {
		const response = await fetch(
			`${API_BASE_URL}/reviews/product_reviews/?product_id=${productId}`
		);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const data = await response.json();
		const reviews = data.results || data;

		displayReviews(reviews);

		// Загружаем форму отзыва
		loadReviewForm();
	} catch (error) {
		console.error('Ошибка загрузки отзывов:', error);
		document.getElementById('reviews-list').innerHTML =
			'<p class="muted">Ошибка загрузки отзывов</p>';
	}
}

// Отображение отзывов
function displayReviews(reviews) {
	const container = document.getElementById('reviews-list');

	if (reviews.length === 0) {
		container.innerHTML = '<p class="muted">Комментариев пока нет.</p>';
		return;
	}

	let html = '<ul class="comments-list">';
	reviews.forEach(review => {
		const date = new Date(review.created_at);
		const formattedDate = date.toLocaleString('ru-RU', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
		});

		html += `
            <li class="comment-item">
                <div class="comment-header">
                    <div class="comment-avatar">${
											review.user_name ? review.user_name[0].toUpperCase() : '?'
										}</div>
                    <div>
                        <p class="comment-user">${review.user_name}</p>
                        <p class="comment-date">${formattedDate}</p>
                    </div>
                </div>
                <p class="comment-rating">Оценка: ${review.rating}</p>
                <p class="comment-text">${review.text}</p>
            </li>
        `;
	});
	html += '</ul>';

	container.innerHTML = html;
}

// Загрузка формы отзыва
async function loadReviewForm() {
	const productId = getProductId();
	if (!productId) return;

	try {
		// Проверяем, может ли пользователь оставить отзыв
		const response = await fetch(
			`${API_BASE_URL}/reviews/product_reviews/?product_id=${productId}`
		);
		const data = await response.json();
		const reviews = data.results || data;

		const container = document.getElementById('review-form-container');

		// В реальном приложении здесь была бы проверка авторизации и существования отзыва
		// Для упрощения показываем форму всегда
		container.innerHTML = `
            <form id="review-form" onsubmit="submitReview(event)">
                <div class="field">
                    <label for="rating">Оценка</label>
                    <select id="rating" name="rating" required>
                        <option value="">Выберите оценку</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                    </select>
                </div>
                <div class="field">
                    <label for="text">Отзыв</label>
                    <textarea id="text" name="text" required></textarea>
                </div>
                <button type="submit" class="login-btn">
                    <span class="btn-text">Отправить</span><span class="btn-loader"></span>
                </button>
            </form>
        `;
	} catch (error) {
		console.error('Ошибка загрузки формы отзыва:', error);
	}
}

// Отправка отзыва
async function submitReview(event) {
	event.preventDefault();

	const productId = getProductId();
	if (!productId) return;

	const formData = {
		rating: parseInt(document.getElementById('rating').value),
		text: document.getElementById('text').value,
		product: parseInt(productId),
	};

	try {
		const csrfToken = getCsrfToken();
		const response = await fetch(`${API_BASE_URL}/reviews/create_review/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': csrfToken,
			},
			credentials: 'include',
			body: JSON.stringify(formData),
		});

		if (response.ok) {
			showNotification('Отзыв успешно добавлен!');
			// Обновляем список отзывов
			loadReviews();
			// Очищаем форму
			document.getElementById('review-form').reset();
		} else {
			const error = await response.json();
			showNotification(
				'Ошибка: ' + (error.error || 'Неизвестная ошибка'),
				'error'
			);
		}
	} catch (error) {
		console.error('Ошибка отправки отзыва:', error);
		showNotification('Ошибка отправки отзыва', 'error');
	}
}
