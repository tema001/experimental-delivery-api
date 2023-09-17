from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, JSON, UUID
from sqlalchemy.orm import relationship

from db_config import Base


class User(Base):
    __tablename__ = "users"

    id = Column('user_id', UUID, primary_key=True)
    username = Column(String)
    password = Column('user_password', String)
    role_id = Column(Integer)
    is_active = Column(Boolean)


class Product(Base):
    __tablename__ = 'products'

    id = Column('product_id', UUID, primary_key=True)
    product_name = Column(String)
    price = Column(Float)
    category_id = Column(UUID, ForeignKey('categories.category_id'))


class Category(Base):
    __tablename__ = 'categories'

    id = Column('category_id', UUID, primary_key=True)
    category_name = Column(String)


class Order(Base):
    __tablename__ = 'orders'

    id = Column('order_id', UUID, primary_key=True)
    customer_name = Column(String, nullable=False)
    delivery_info_id = Column(UUID, ForeignKey('delivery_info.delivery_info_id'), nullable=False)
    data = Column(JSON)
    order_status = Column(String)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    delivery_info = relationship('DeliveryInfo', back_populates='order', lazy="joined")


class OrderEvent(Base):
    __tablename__ = 'order_events'

    id = Column('order_event_id', UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey('orders.order_id'), nullable=False)
    name = Column(String, nullable=False)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True))


class DeliveryInfo(Base):
    __tablename__ = 'delivery_info'

    id = Column('delivery_info_id', UUID, primary_key=True)
    address = Column(String)
    courier_id = Column(UUID, ForeignKey('users.user_id'))

    order = relationship('Order', back_populates='delivery_info')

# Base.metadata.create_all(bind=engine)

