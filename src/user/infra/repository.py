from typing import Mapping

from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db_config import get_session
from models import User

from shared.domain.entity import Entity
from user.domain.entity import UserEntity, Role


class UserDataMapper:
    @staticmethod
    def model_to_entity(instance: User) -> UserEntity:
        return UserEntity(id=instance.id,
                          username=instance.username,
                          password=instance.password,
                          role=Role.from_id(instance.role_id),
                          is_active=instance.is_active)

    @staticmethod
    def entity_to_model(entity: UserEntity):
        pass


class UserRepository:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self._db = db

    async def get_by_name(self, username: str) -> UserEntity | None:
        stmt = select(User).where(User.username == username)
        res = await self._db.execute(stmt)
        user = res.scalar_one_or_none()

        if user is None:
            return user
        return UserDataMapper.model_to_entity(user)

    async def add(self, entity: Entity):
        pass