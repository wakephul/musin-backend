import uuid

from api.api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float

class Network(db.Model):

    __tablename__ = "network"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    name = Column(String(100), nullable=False)
    sides = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, code: str, name: str, sides: int):
        self.code = code
        self.name = name
        self.sides = sides

    @staticmethod
    def create(name: str, sides: int):
        code = str(uuid.uuid4())
        to_create = Network(code=code, name=name, sides=sides)
        db.session.add(to_create)
        db.session.commit()
        return code
    
    @staticmethod
    def to_dict(network):
        return {
            'code': network.code,
            'name': network.name,
            'sides': network.sides,
            'created_at': network.created_at
        }

    @staticmethod
    def get_one(code):
        result = Network.query.get(code)
        if not result:
            return None
        return Network.to_dict(result)
    
    @staticmethod
    def get_name(code):
        result = Network.query.get(code)
        if not result:
            return None
        return result.name

    @staticmethod
    def get_all():
        return [
            Network.to_dict(i)
            for i in Network.query.all()
        ]

class NetworkParameter(db.Model):

    __tablename__ = "network_parameter"

    network_code = Column(String(36), ForeignKey("network.code"), primary_key=True)
    name = Column(String(100), nullable=False, primary_key=True)
    value = Column(Float, nullable=False)

    def __init__(self, network_code: str, name: str, value: float):
        self.network_code = network_code
        self.name = name
        self.value = value

    @staticmethod
    def create(network_code: str, name: str, value: float):
        to_create = NetworkParameter(network_code, name, value)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def to_dict(network_parameter):
        return {
            'network_code': network_parameter.network_code,
            'name': network_parameter.name,
            'value': network_parameter.value
        }

    @staticmethod
    def get_one(code):
        result = NetworkParameter.query.get(code)
        if not result:
            return None
        return NetworkParameter.to_dict(result)
    
    @staticmethod
    def get_by_network_code(code):
        return [
            NetworkParameter.to_dict(i)
            for i in NetworkParameter.query.filter_by(network_code=code).all()
        ]

    @staticmethod
    def get_all():
        return [
            NetworkParameter.to_dict(i)
            for i in NetworkParameter.query.all()
        ]