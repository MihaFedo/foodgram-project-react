# Generated by Django 3.2.19 on 2023-05-24 22:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_ingredientrecipe_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_tagrecipe', to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='tagrecipe',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tag_tagrecipe', to='recipes.tag'),
        ),
    ]
