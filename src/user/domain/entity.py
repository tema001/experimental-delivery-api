from user.domain.value_obj import RoleName
from shared.domain.entity import Entity

from dataclasses import dataclass


@dataclass
class Role(Entity):
    value: RoleName

    @classmethod
    def from_id(cls, role_id: int):
        value = None
        if role_id == 1:
            value = RoleName.ADMIN
        elif role_id == 2:
            value = RoleName.MODERATOR
        elif role_id == 3:
            value = RoleName.CUSTOMER

        return cls(id=role_id, value=value)


@dataclass
class AuthorizedUserEntity(Entity):
    username: str
    role: RoleName

    def verify_admin_access(self) -> bool:
        return self.role.value == RoleName.ADMIN

    def verify_moderator_access(self) -> bool:
        return self.role.value == RoleName.MODERATOR


@dataclass
class UserEntity(AuthorizedUserEntity):
    username: str
    password: str
    role: Role
    is_active: True
