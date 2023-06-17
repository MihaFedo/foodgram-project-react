from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
import os

from ..models import Recipe


@receiver(post_delete, sender=Recipe)
def post_save_image(sender, instance, *args, **kwargs):
    """Удаление картинки блюда из хранилища при удалении рецепта."""
    instance.image.delete(save=False)


@receiver(pre_save, sender=Recipe)
def pre_save_image(sender, instance, *args, **kwargs):
    """Удаление старой картинки блюда при изменении рецепта"""
    try:
        old_img = sender.objects.get(id=instance.id).image.path
        new_img = instance.image.path
        if new_img != old_img:
            if os.path.exists(old_img):
                os.remove(old_img)
    except ObjectDoesNotExist:
        pass
