from sqlalchemy import Column, Integer, String, DateTime
from Storage.base import Base
import datetime


class Pickup(Base):
    """ Pickup orders """

    __tablename__ = "pickup"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    order_id = Column(String(250), nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    preparation_time = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, customer_id, order_id):
        """ Initializes a pickup order """
        self.customer_id = customer_id
        self.order_id = order_id
        self.purchase_date = datetime.datetime.now()
        self.preparation_time = self.purchase_date + datetime.timedelta(minutes=15)
        self.date_created = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        """ Dictionary Representation of a pickup order """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['order_id'] = self.order_id
        dict['purchase_date'] = self.purchase_date
        dict['preparation_time'] = self.preparation_time
        dict['date_created'] = self.date_created
        return dict
