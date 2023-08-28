from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from db_config import get_session
from models import User

from .utils import authorize_user, decode_token
from exceptions import DecodeTokenError, UserIsInactive, NoPermissionByRole

from jose import JWTError, ExpiredSignatureError

oauth2_scheme = OAuth2PasswordBearer('token')


async def get_token(form_data: OAuth2PasswordRequestForm = Depends(),
                    db: AsyncSession = Depends(get_session)) -> str | None:
    stmt = select(User).where(User.username == form_data.username)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if user:
        if user.is_active is False:
            raise UserIsInactive

        return authorize_user(form_data.password, user)


async def get_token_data(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return decode_token(token)
    except ExpiredSignatureError:
        raise DecodeTokenError('Authorization token has expired')
    except JWTError:
        raise DecodeTokenError('Invalid token authorization')


async def verify_rw(token_data: dict = Depends(get_token_data)) -> bool:
    if verify_admin_access(token_data) or verify_moderator_access(token_data):
        return True
    else:
        raise NoPermissionByRole


def verify_admin_access(data: dict) -> bool:
    return data['role'] == 1


def verify_moderator_access(data: dict) -> bool:
    return data['role'] == 2
