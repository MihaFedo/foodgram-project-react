from django.db.models.signals import post_delete
from django.dispatch import receiver

from ..models import Recipe


@receiver(post_delete, sender=Recipe)
def post_save_image(sender, instance, *args, **kwargs):
    """Удаление картинки блюда из хранилища при удалении рецепта."""
    instance.image.delete(save=False)
