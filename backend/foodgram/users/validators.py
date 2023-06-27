import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            _(f'{value} служебное имя!!')
        )
    if not re.match(r'^[\w.@+-]+\Z', value):
        forbidden_symb = ' '.join(
            set(re.sub(r'^[\w.@+-]+\Z', '', _) for _ in value)
        )
        raise ValidationError(_(
            f'{value} содержит запрещенные символы: ({forbidden_symb}).'
            'Имя пользователя может содержать только буквы, цифры, '
            'а также @/./+/-/_ символы.'
        ))
