// Функции для личного кабинета
document.addEventListener('DOMContentLoaded', function () {
	loadOrders();
});

// Загрузка заказов пользователя
async function loadOrders() {
	try {
		const response = await fetch(`${API_BASE_URL}/orders/my_orders/`);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const orders = await response.json();
		displayOrders(orders);
	} catch (error) {
		console.error('Ошибка загрузки заказов:', error);
		document.getElementById('orders-container').innerHTML =
			'<div class="alert alert-danger">Ошибка загрузки заказов</div>';
	}
}

// Отображение заказов
function displayOrders(orders) {
	const container = document.getElementById('orders-container');
	if (!container) return;

	if (orders.length === 0) {
		container.innerHTML = '<p class="muted">У вас пока нет заказов</p>';
		return;
	}

	let html = '<div class="orders-list">';
	orders.forEach(order => {
		const date = new Date(order.date_order);
		const formattedDate = date.toLocaleString('ru-RU', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
		});

		html += `
            <div class="order-card">
                <h3>Заказ #${order.id}</h3>
                <p class="order-date">Дата: ${formattedDate}</p>
                <p class="order-status">Статус: ${order.status}</p>
                <div class="order-items">
                    <h4>Товары:</h4>
                    ${order.order_items
											.map(
												item => `
                        <div class="order-item">
                            <span>${item.product_name}</span>
                            <span>${item.quantity} x ${
													item.product_price
												} ₽ = ${item.subtotal.toFixed(2)} ₽</span>
                        </div>
                    `
											)
											.join('')}
                </div>
                <p class="order-total">Итого: ${order.total.toFixed(2)} ₽</p>
            </div>
        `;
	});
	html += '</div>';

	container.innerHTML = html;
}


