from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from user.application.service import UserService

router = APIRouter()


@router.get('/token')
async def auth(form_data: OAuth2PasswordRequestForm = Depends(),
               user_service: UserService = Depends()):
    jwt_token = await user_service.authorize_user(form_data.username, form_data.password)
    return {'token_type': 'Bearer', 'access_token': jwt_token}
