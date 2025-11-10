from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ShopMainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop_main'
    
    def ready(self):
       
        from . import signals 
        post_migrate.connect(
            signals.create_manager_group,
            sender=self
        )