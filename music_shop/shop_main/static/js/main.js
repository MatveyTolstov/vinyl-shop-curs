// Функции для главной страницы
document.addEventListener('DOMContentLoaded', function () {
	loadGenres();
});

async function loadGenres() {
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

		const container = document.getElementById('genres-container');
		if (!container) return;

		container.innerHTML = '';

		genres.forEach(genre => {
			const genreCard = document.createElement('div');
			genreCard.className = 'category-card';
			genreCard.innerHTML = `
                <h3>${genre.genre_name}</h3>
                <p>${genre.description}</p>
            `;
			container.appendChild(genreCard);
		});
	} catch (error) {
		console.error('Ошибка загрузки жанров:', error);
		const container = document.getElementById('genres-container');
		if (container) {
			container.innerHTML =
				'<div class="alert alert-danger">Ошибка загрузки жанров: ' +
				error.message +
				'</div>';
		}
	}
}
