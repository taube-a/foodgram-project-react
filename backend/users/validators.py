from django.core.exceptions import ValidationError


def validate_username(username):
    """Валидация имени пользователя."""
    if username.lower() == 'me':
        raise ValidationError(
            'Невозможно создать пользователя с логином'
            ' "%s" - это запрещено.' % username)
    return username
