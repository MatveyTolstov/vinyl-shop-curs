"""Утилиты для логирования действий пользователей"""
from .models import LogEntry


def create_log_entry(
    action,
    user=None,
    description="",
    ip_address=None,
    user_agent="",
    order=None,
    product=None,
):
    """
    Создает запись в логе
    
    Args:
        action: Тип действия (из LogEntry.ACTION_CHOICES)
        user: Пользователь (может быть None для анонимных)
        description: Описание действия
        ip_address: IP адрес пользователя
        user_agent: User-Agent браузера
        order: Связанный заказ (опционально)
        product: Связанный товар (опционально)
    """
    try:
        LogEntry.objects.create(
            user=user,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            order=order,
            product=product,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка создания лога: {e}")

