from shared.domain.events import DomainEvent


class CreateNewOrder(DomainEvent):
    ...


class AddItemsToOrder(DomainEvent):
    ...


class UpdateOrderItems(DomainEvent):
    ...


class UpdateOrderAddress(DomainEvent):
    ...


class StartOrder(DomainEvent):
    ...


class ReadyToDelivery(DomainEvent):
    ...


class Delivering(DomainEvent):
    ...


class CompleteOrder(DomainEvent):
    ...


class CancelOrder(DomainEvent):
    ...
