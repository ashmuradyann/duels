from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import CustomUser

def get_user_from_token(token):
    try:
        untyped_token = UntypedToken(token)
        user_id = untyped_token['user_id']
        user = CustomUser.objects.get(id=user_id)
        return user
    except (InvalidToken, TokenError, CustomUser.DoesNotExist):
        return None