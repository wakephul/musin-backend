from ..api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

class Network(db.Model):

    __tablename__ = "network"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def create(name: str):
        to_create = Network(name)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'id': i.id, 'name': i.name, 'created_at': i.created_at}
                for i in Network.query.order_by('id').all()]

class NetworkParameter(db.Model):

    __tablename__ = "network_parameter"

    network_id = Column(Integer, ForeignKey("network.id"), primary_key=True)
    name = Column(String(100), nullable=False, primary_key=True)
    value = Column(Float, nullable=False)

    def __init__(self, network_id: int, name: str, value: float):
        self.network_id = network_id
        self.name = name
        self.value = value

    @staticmethod
    def create(network_id: int, name: str, value: float):
        to_create = NetworkParameter(network_id, name, value)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'network_id': i.network_id, 'name': i.name, 'value': i.value}
                for i in NetworkParameter.query.order_by('id').all()]