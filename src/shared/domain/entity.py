from dataclasses import dataclass


@dataclass
class Entity:
    id: int

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return other.id == self.id
        return False


@dataclass
class AggregateRoot(Entity):
    pass
