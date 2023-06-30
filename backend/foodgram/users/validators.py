import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def check_string(string):
    '''Заготовка для проверки username и доп.проверки email.'''
    if not re.match(r'^[\w.@+-]+\Z', string):
        forbidden_symb = ' '.join(set(re.sub(r'[\w.@+-]', '', string)))
        raise ValidationError(_(
            f'{string} содержит запрещенные символы: ({forbidden_symb}).'
        ))

def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            _(f'{value} служебное имя!!')
        )
    check_string(value)

def validate_email(value):
    check_string(value)
