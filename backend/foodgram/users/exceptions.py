from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError


class NotFoundAuthor(ValidationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Такого автора не существует.')
    default_code = 'invalid'
