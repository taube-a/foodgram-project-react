from django.core.exceptions import ValidationError


def validate_username(username):
    """Валидация имени пользователя."""
    if username == 'me':
        raise ValidationError(
            'Невозможно создать пользователя с логином'
            ' "me" - это запрещено.')
    return username
