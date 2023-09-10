from dataclasses import dataclass
import uuid


class EntityId:
    @classmethod
    def next_id(cls):
        return uuid.uuid4()


@dataclass
class Entity:
    id: EntityId

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return other.id == self.id
        return False


@dataclass
class AggregateRoot(Entity):
    pass
