from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.dispatch import receiver
from .models import Product

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate the product cache when a product is created, updated, or deleted.
    """
    cache.delete_pattern('*product_list*')

