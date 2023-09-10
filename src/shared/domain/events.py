from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from shared.domain.entity import EntityId


@dataclass(init=False)
class DomainEvent:
    id: EntityId
    aggregate_id: EntityId
    name: str
    data: Mapping | None
    created_at: datetime

    def __init__(self, aggregate_id: EntityId, data: Mapping = None):
        self.id = EntityId.next_id()
        self.aggregate_id = aggregate_id
        self.name = self.__class__.__name__
        self.data = data
        self.created_at = datetime.utcnow()
