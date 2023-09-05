from enum import Enum


class RoleName(str, Enum):
    CUSTOMER = 'CUSTOMER'
    ADMIN = 'ADMIN'
    MODERATOR = 'MODERATOR'
