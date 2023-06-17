from django.apps import AppConfig


class RecipesConfig(AppConfig):
    name = 'recipes'

    def ready(self):
        from .signals import recipe_signals
        print('---------------------', recipe_signals.__name__)
