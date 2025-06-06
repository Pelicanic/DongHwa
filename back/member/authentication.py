from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from api.models import User

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get("user_id")
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise InvalidToken({"detail": "User not found", "code": "user_not_found"})
