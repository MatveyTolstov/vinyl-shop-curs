from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging
from .models import Order, Review, OrderItem
from .logger_utils import create_log_entry


logger = logging.getLogger(__name__)


def create_manager_group(sender, **kwargs):
    try:
        Group.objects.create(name='Manager')
        logger.info("Manager group created")
    except IntegrityError:
        logger.info("Manager group already exists")


@receiver(post_save, sender=Order)
def log_order_updated(sender, instance, created, **kwargs):
    """Логирует обновление заказа"""
    if not created:
        if hasattr(instance, '_old_status') and instance._old_status != instance.status:
            create_log_entry(
                action='order_updated',
                user=instance.user,
                description=f"Статус заказа #{instance.id} изменен с '{instance._old_status}' на '{instance.status}'",
                order=instance,
            )


@receiver(post_save, sender=Review)
def log_review_created(sender, instance, created, **kwargs):
    """Логирует создание отзыва"""
    if created:
        request = kwargs.get('request', None)
        ip_address = None
        user_agent = ""
        
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        
        create_log_entry(
            action='review_created',
            user=instance.user,
            description=f"Создан отзыв на товар '{instance.product.product_name}' с оценкой {instance.rating}",
            ip_address=ip_address,
            user_agent=user_agent,
            product=instance.product,
        )