from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from user.domain.entity import UserEntity

SECRET_KEY = 'afa464fec3cef011676bd4ff9ae375a63a4184b69f9c78b5cf6694946a302c82'
ALGORITHM = 'HS256'
crypt_context = CryptContext(['bcrypt'])


def generate_jwt_token(input_password: str, user: UserEntity) -> str | None:
    if crypt_context.verify(input_password, user.password):
        data = {
            'id': str(user.id),
            'username': user.username,
            'role': user.role.value
        }
        expire = datetime.utcnow() + timedelta(weeks=1)
        data['exp'] = expire
        return jwt.encode(data, SECRET_KEY, ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, ALGORITHM)
