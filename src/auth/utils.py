from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from models import User

SECRET_KEY = 'afa464fec3cef011676bd4ff9ae375a63a4184b69f9c78b5cf6694946a302c82'
ALGORITHM = 'HS256'
crypt_context = CryptContext(['bcrypt'])


def _create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(weeks=1)
    data['exp'] = expire

    return jwt.encode(data, SECRET_KEY, ALGORITHM)


def authorize_user(input_password: str, user: User) -> str | None:
    if crypt_context.verify(input_password, user.password):
        return _create_access_token({'username': user.username, 'role': user.role_id})


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, ALGORITHM)
