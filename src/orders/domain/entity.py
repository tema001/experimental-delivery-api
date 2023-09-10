from datetime import datetime

from shared.domain.entity import EntityId, Entity, AggregateRoot
from shared.domain.events import DomainEvent
from .exceptions import NoItemsInOrderError, OrderStatusTransitionError, InappropriateOrderStatusError
from .value_obj import OrderItem, Status
import orders.domain.events as events

from dataclasses import dataclass, field


@dataclass
class DeliveryInfoEntity(Entity):
    address: str
    courier_id: int = None


@dataclass
class OrderEntity(AggregateRoot):
    customer_name: str
    delivery_info: DeliveryInfoEntity
    order_items: list[OrderItem]
    status: Status
    created_at: datetime
    total_price: float = 0.0

    events: list[DomainEvent] = field(default_factory=list, compare=False)

    @classmethod
    def create(cls, customer_name: str, address: str, items: list):
        new_id = EntityId.next_id()
        ev = [events.CreateNewOrder(new_id)]
        return cls(id=new_id,
                   customer_name=customer_name,
                   delivery_info=DeliveryInfoEntity(id=EntityId.next_id(),
                                                    address=address),
                   order_items=items,
                   status=Status.CREATED,
                   created_at=datetime.utcnow(),
                   events=ev)

    @property
    def items_as_model_data(self) -> dict:
        return {'total_price': self.total_price,
                'products': [x.as_dict() for x in self.order_items]
        }

    def calc_total_price(self):
        self.total_price = sum((x.price * x.quantity for x in self.order_items))

    def _is_possible_to_update(self) -> bool:
        if self.status in (Status.CANCELED, Status.DELIVERING, Status.COMPLETED):
            return False
        return True

    def update_items(self, new_items: list[OrderItem]):
        if not self._is_possible_to_update():
            raise InappropriateOrderStatusError

        self.order_items = new_items
        self.calc_total_price()
        self.events.append(
            events.UpdateOrderItems(self.id, data=self.items_as_model_data)
        )

    def update_address(self, new_address: str):
        if not self._is_possible_to_update():
            raise InappropriateOrderStatusError

        self.delivery_info.address = new_address

    def begin(self):
        if not self.order_items or self.total_price < 1:
            raise NoItemsInOrderError

        if self.status != Status.CREATED:
            raise OrderStatusTransitionError(Status.STARTED, self.status, Status.CREATED)

        self.status = Status.STARTED
        self.events.append(events.StartOrder(self.id))

    def ready(self):
        if self.status != Status.STARTED:
            raise OrderStatusTransitionError(Status.READY_TO_DELIVERY, self.status, Status.STARTED)

        self.status = Status.READY_TO_DELIVERY
        self.events.append(events.ReadyToDelivery(self.id))

    def delivery(self):
        if self.status != Status.READY_TO_DELIVERY:
            raise OrderStatusTransitionError(Status.DELIVERING, self.status, Status.READY_TO_DELIVERY)

        self.status = Status.DELIVERING
        self.events.append(events.Delivering(self.id))

    def complete(self):
        if self.status != Status.DELIVERING:
            raise OrderStatusTransitionError(Status.COMPLETED, self.status, Status.DELIVERING)

        self.status = Status.COMPLETED
        self.events.append(events.CompleteOrder(self.id))

    def cancel(self):
        if self.status == Status.COMPLETED:
            raise

        self.status = Status.CANCELED
        self.events.append(events.CancelOrder(self.id))
