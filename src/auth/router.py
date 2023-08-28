from fastapi import APIRouter, Depends
from exceptions import BadCredentialsError

from .service import get_token

router = APIRouter()


@router.get('/token')
async def auth(jwt_token: str = Depends(get_token)):
    if jwt_token:
        return {'token_type': 'Bearer', 'access_token': jwt_token}
    else:
        raise BadCredentialsError()
