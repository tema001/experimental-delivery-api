from fastapi import status
from starlette.exceptions import HTTPException


class OrderStatusTransitionError(HTTPException):
    def __init__(self, actual, expected):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f'Unable to change order status to {expected}, the status is {actual}')


class OrderNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail='Order is absent')


class ProductNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail='Product is absent')


class UserIsInactive(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail='User is inactive')


class BadCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Incorrect username or password",
                         headers={"WWW-Authenticate": "Bearer"})


class DecodeTokenError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=detail,
                         headers={"WWW-Authenticate": "Bearer"})


class NoPermissionByRole(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail='No permission to do it')
