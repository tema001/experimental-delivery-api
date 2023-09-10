from starlette import status
from starlette.exceptions import HTTPException


class NoItemsInOrderError(Exception):
    def __repr__(self):
        return 'Items list for this order is empty'


class InappropriateOrderStatusError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail='Unable to update order due to status')


class OrderNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail='Order is absent')


class OrderStatusTransitionError(HTTPException):
    def __init__(self, new, actual, expected):
        msg = f'Unable to change the order status to {new}, the status now is {actual} but expected {expected}'
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=msg)
