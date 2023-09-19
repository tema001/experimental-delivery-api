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
    updated_at: datetime
    total_price: float = 0.0

    events: list[DomainEvent] = field(default_factory=list, compare=False)

    @classmethod
    def create(cls, customer_name: str, address: str, items: list):
        new_id = EntityId.next_id()
        time_now = datetime.utcnow()
        ev = [events.CreateNewOrder(new_id)]
        return cls(id=new_id,
                   customer_name=customer_name,
                   delivery_info=DeliveryInfoEntity(id=EntityId.next_id(),
                                                    address=address),
                   order_items=items,
                   status=Status.CREATED,
                   created_at=time_now,
                   updated_at=time_now,
                   events=ev)

    @property
    def items_as_model_data(self) -> dict:
        return {'total_price': self.total_price,
                'products': [x.as_dict() for x in self.order_items]
        }

    def calc_total_price(self):
        self.total_price = sum((x.price * x.quantity for x in self.order_items))

    def update_time(self):
        self.updated_at = datetime.utcnow()

    def _is_possible_to_update(self) -> bool:
        if self.status in (Status.CANCELED, Status.DELIVERING, Status.COMPLETED):
            return False
        return True

    def update_items(self, new_items: list[OrderItem]):
        if not self._is_possible_to_update():
            raise InappropriateOrderStatusError

        self.order_items = new_items
        self.calc_total_price()
        self.update_time()
        self.events.append(
            events.UpdateOrderItems(self.id, data=self.items_as_model_data)
        )

    def update_address(self, new_address: str):
        if not self._is_possible_to_update():
            raise InappropriateOrderStatusError

        self.delivery_info.address = new_address

    def _transit_status(self, new: Status, expected: Status):
        if self.status != expected:
            raise OrderStatusTransitionError(new, self.status, expected)
        self.status = new
        self.update_time()

    def begin(self):
        if not self.order_items or self.total_price < 1:
            raise NoItemsInOrderError

        self._transit_status(Status.STARTED, Status.CREATED)
        self.events.append(events.StartOrder(self.id))

    def ready(self):
        self._transit_status(Status.READY_TO_DELIVERY, Status.STARTED)
        self.events.append(events.ReadyToDelivery(self.id))

    def delivery(self):
        self._transit_status(Status.DELIVERING, Status.READY_TO_DELIVERY)
        self.events.append(events.Delivering(self.id))

    def complete(self):
        self._transit_status(Status.COMPLETED, Status.DELIVERING)
        self.events.append(events.CompleteOrder(self.id))

    def cancel(self):
        if self.status == Status.COMPLETED:
            raise

        self.status = Status.CANCELED
        self.update_time()
        self.events.append(events.CancelOrder(self.id))
