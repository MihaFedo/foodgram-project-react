import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_slug(value):
    if not re.match(r'^[-a-zA-Z0-9_]+$', value):
        forbidden_symb = ' '.join(
            set(re.sub(r'^[-a-zA-Z0-9_]+$', '', _) for _ in value)
        )
        raise ValidationError(_(
            f'{value} содержит запрещенные символы: ({forbidden_symb}).'
        ))
