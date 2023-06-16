from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from ..models import Recipe

@receiver(post_delete, sender=Recipe)
def post_save_image(sender, instance, *args, **kwargs):
    """Удаление картинки блюда из хранилища при удалении рецепта."""
    try:
        instance.image.delete(save=False)
    except:
        pass

@receiver(pre_save, sender=Recipe)
def pre_save_image(sender, instance, *args, **kwargs):
    """Удаление старой картинки блюда при изменении рецепта"""
    try:
        old_img = instance.__class__.objects.get(id=instance.id).image.path
        try:
            new_img = instance.image.path
        except:
            new_img = None
        if new_img != old_img:
            import os
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass
