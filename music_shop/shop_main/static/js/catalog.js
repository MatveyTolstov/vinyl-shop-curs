document.addEventListener('DOMContentLoaded', async function () {
	loadGenres();
	loadArtists();
	loadCartFromCookies();
	// Гарантируем, что избранное подгружено до рендера, чтобы сердечки были корректны
	if (typeof ensureFavoritesLoaded === 'function') {
		try { await ensureFavoritesLoaded(); } catch (e) {}
	}
	loadProductsCatalog();
});

function displayProducts(products) {
	const container = document.getElementById('products-container');
	if (!container) return;

	if (products.length === 0) {
		container.innerHTML = `
            <div class="no-products">
                <h3>Товары не найдены</h3>
                <p>Попробуйте изменить параметры фильтрации</p>
            </div>
        `;
		return;
	}

	container.innerHTML = '<div class="products-grid"></div>';
	const grid = container.querySelector('.products-grid');

	products.forEach(product => {
		const productCard = document.createElement('div');
		productCard.className = 'product-card';
		productCard.innerHTML = `
            <button 
                class="fav-btn" 
                aria-label="Избранное" 
                data-product-id="${product.id}"
                type="button"
                style="position:absolute; right:10px; top:10px; background:#fff; border:1px solid #e5e7eb; border-radius:9999px; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; z-index:2; pointer-events:auto;">
                <span class="heart" style="font-size:16px;">♡</span>
            </button>
            <div class="product-image" onclick="window.location.href='/product/${
							product.id
						}/'">
                ${
									product.picture
										? `<img src="${product.picture}" alt="${product.product_name}">`
										: '<div class="vinyl-placeholder">🎵</div>'
								}
            </div>
            <h3>${product.product_name}</h3>
            <p class="artist">${product.artist_name}</p>
            <p class="genre">${product.genre_name}</p>
            <p class="price">${product.price} ₽</p>
            <button 
                class="add-to-cart-btn" 
                onclick="addToCart(${product.id})"
                ${product.stock_quantity <= 0 ? 'disabled' : ''}
            >
                ${
									product.stock_quantity <= 0
										? 'Нет в наличии'
										: 'Добавить в корзину'
								}
            </button>
        `;
		grid.appendChild(productCard);

		// Инициализация состояния избранного (с защитой, если API недоступен)
		const favBtn = productCard.querySelector('.fav-btn');
		const heart = favBtn.querySelector('.heart');
		try {
			if (typeof isFavorite === 'function' && isFavorite(product.id)) {
				heart.textContent = '❤';
				heart.style.color = '#dc2626';
			}
		} catch (e) {}
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
	});
}

async function applyFilters() {
	const search = document.getElementById('search').value;
	const genre = document.getElementById('genre').value;
	const artist = document.getElementById('artist').value;
	const minPrice = document.getElementById('min_price').value;
	const maxPrice = document.getElementById('max_price').value;
	const sort = document.getElementById('sort').value;

	const filters = {};
	if (search) filters.search = search;
	if (genre) filters.genre = genre;
	if (artist) filters.artist = artist;
	if (minPrice) filters.min_price = minPrice;
	if (maxPrice) filters.max_price = maxPrice;
	if (sort) filters.sort = sort;

	showSpinner('products-container');

	try {
		const products = await loadProducts(filters);
		displayProducts(products);
	} catch (error) {
		console.error('Ошибка применения фильтров:', error);
		showError('products-container', 'Ошибка применения фильтров');
	}
}

function clearFilters() {
	document.getElementById('filter-form').reset();
	loadProductsCatalog();
}

async function loadProductsCatalog() {
	showSpinner('products-container');

	try {
		const products = await loadProducts();
		displayProducts(products);
	} catch (error) {
		console.error('Ошибка загрузки товаров:', error);
		showError('products-container', 'Ошибка загрузки товаров');
	}
}
