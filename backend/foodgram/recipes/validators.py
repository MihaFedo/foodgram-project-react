import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_slug(value):
    if not re.match(r'^[-a-zA-Z0-9_]+$', value):
        raise ValidationError(_(f'{value} содержит запрещенные символы!'))
