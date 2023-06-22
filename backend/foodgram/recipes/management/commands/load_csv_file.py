import os

import pandas as pd
from django.core.management import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient, Measurement

path_ingredients = os.path.join(BASE_DIR, 'data/ingredients.csv')
print(path_ingredients)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # считываем исходную таблицу
        df = pd.read_csv(
            path_ingredients,
            names=['name', 'meas_name']
        )
        # убираем дубли ингредиентов
        df = df[(df.name != 'пекарский порошок') | (df.meas_name != 'г')]
        df = df[(df.name != 'стейк семги') | (df.meas_name != 'шт.')]

        # готовим таблицу с measurement_units + добавляем id
        unique_meas_list = sorted(df.meas_name.unique())
        df_meas_units = pd.DataFrame(unique_meas_list, columns=['meas_name'])
        df_meas_units['id'] = range(1, len(df_meas_units) + 1)

        # готовим таблицу с ingredients + добавляем id + id measurement_units
        df_ingredients = pd.merge(
            df,
            df_meas_units,
            how='left',
            left_on='meas_name',
            right_on='meas_name',
        )
        df_ingredients.rename(
            columns={'id': 'measurement_unit'},
            inplace=True
        )
        df_ingredients.drop(['meas_name'], axis=1, inplace=True)
        df_ingredients['id'] = range(1, len(df_ingredients) + 1)

        # запись в Measurement
        df_meas_units.rename(columns={'meas_name': 'name'}, inplace=True)
        df_meas_units = df_meas_units.to_dict('records')

        for row in df_meas_units:
            Measurement.objects.update_or_create(
                id=row['id'],
                name=row['name'],
            )

        # запись в Ingredient
        df_ingredients = df_ingredients.to_dict('records')

        for row in df_ingredients:
            Ingredient.objects.update_or_create(
                id=row['id'],
                name=row['name'],
                measurement_unit=Measurement.objects.get(
                    id=row['measurement_unit']
                ),
            )
