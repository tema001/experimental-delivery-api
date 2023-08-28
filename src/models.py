from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime

from db_config import Base


class User(Base):
    __tablename__ = "users"

    id = Column('user_id', Integer, primary_key=True)
    username = Column(String)
    password = Column('user_password', String)
    role_id = Column(Integer)
    is_active = Column(Boolean)


class Product(Base):
    __tablename__ = 'products'

    id = Column('product_id', Integer, primary_key=True)
    product_name = Column(String)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('categories.category_id'))


class Category(Base):
    __tablename__ = 'categories'

    id = Column('category_id', Integer, primary_key=True)
    category_name = Column(String)


class Order(Base):
    __tablename__ = 'orders'

    id = Column('order_id', Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    delivery_info_id = Column(Integer, ForeignKey('delivery_info.delivery_info_id'), nullable=False)
    total_price = Column(Float)
    created_at = Column(DateTime(timezone=True))


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column('order_item_id', Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    quantity = Column(Integer)
    price = Column(Float)


class OrderStatus(Base):
    __tablename__ = 'order_statuses'

    id = Column('order_status_id', Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    timestampz = Column(DateTime(timezone=True))
    status = Column(String)


class DeliveryInfo(Base):
    __tablename__ = 'delivery_info'

    id = Column('delivery_info_id', Integer, primary_key=True)
    address = Column(String)
    courier_id = Column(Integer, ForeignKey('users.user_id'))

# Base.metadata.create_all(bind=engine)

