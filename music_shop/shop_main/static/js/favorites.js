document.addEventListener('DOMContentLoaded', async function () {
	showSpinner('favorites-container');
	await ensureFavoritesLoaded();
	const products = await fetchFavoritesProducts();
	renderFavorites(products);
});

function renderFavorites(products) {
	const container = document.getElementById('favorites-container');
	if (!container) return;

	if (!products || products.length === 0) {
		container.innerHTML = `
            <div class="no-products">
                <h3>В избранном пусто</h3>
                <p><a href="/catalog/">Перейти в каталог</a></p>
            </div>
        `;
		return;
	}

	container.innerHTML = '<div class="products-grid"></div>';
	const grid = container.querySelector('.products-grid');

	products.forEach(product => {
		const card = document.createElement('div');
		card.className = 'product-card';
		card.innerHTML = `
            <button 
                class="fav-btn" 
                aria-label="Избранное" 
                data-product-id="${product.id}"
                type="button"
                style="position:absolute; right:10px; top:10px; background:#fff; border:1px solid #e5e7eb; border-radius:9999px; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; z-index:2; pointer-events:auto;">
                <span class="heart" style="font-size:16px;color:#dc2626;">❤</span>
            </button>
            <div class="product-image" onclick="window.location.href='/product/${product.id}/'">
                ${product.picture ? `<img src="${product.picture}" alt="${product.product_name}">` : '<div class="vinyl-placeholder">🎵</div>'}
            </div>
            <h3>${product.product_name}</h3>
            <p class="artist">${product.artist_name}</p>
            <p class="genre">${product.genre_name}</p>
            <p class="price">${product.price} ₽</p>
            <button class="add-to-cart-btn" onclick="addToCart(${product.id})">
                Добавить в корзину
            </button>
        `;
		grid.appendChild(card);

		const favBtn = card.querySelector('.fav-btn');
		const heart = favBtn.querySelector('.heart');
		favBtn.addEventListener('click', async (e) => {
			e.stopPropagation();
			const result = await toggleFavorite(product.id);
			if (result.status === 'removed') {
				card.remove();
				if (!grid.children.length) {
					renderFavorites([]);
				}
			} else if (result.status === 'added') {
				heart.textContent = '❤';
				heart.style.color = '#dc2626';
			}
		});
	});
}


