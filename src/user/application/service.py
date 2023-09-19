from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError

from user.infra.repository import UserRepository
from user.domain.entity import AuthorizedUserEntity
from .utils import generate_jwt_token, decode_token
from exceptions import UserIsInactive, BadCredentialsError, DecodeTokenError, NoPermissionByRole

oauth2_scheme = OAuth2PasswordBearer('token')


class UserService:

    def __init__(self, repo: UserRepository = Depends()):
        self._repo = repo

    async def authorize_user(self, username: str, password: str) -> str | None:
        user = await self._repo.get_by_name(username)

        if user is None:
            raise
        if user.is_active is False:
            raise UserIsInactive

        token = generate_jwt_token(password, user)

        if token is None:
            raise BadCredentialsError()
        return token

    @staticmethod
    def get_user_from_token(token: str = Depends(oauth2_scheme)) -> AuthorizedUserEntity:
        try:
            data = decode_token(token)
            return AuthorizedUserEntity(id=data.get('id'),
                                        username=data.get('username'),
                                        role=data.get('role'))
        except ExpiredSignatureError:
            raise DecodeTokenError('Authorization token has expired')
        except JWTError:
            raise DecodeTokenError('Invalid token authorization')

    @staticmethod
    def is_rw_access(user: AuthorizedUserEntity) -> bool:
        if user.verify_admin_access() or user.verify_moderator_access():
            return True
        raise NoPermissionByRole
