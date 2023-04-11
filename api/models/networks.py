import uuid

from api.api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float

class Network(db.Model):

    __tablename__ = "network"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    @staticmethod
    def create(name: str):
        code = str(uuid.uuid4())
        to_create = Network(code=code, name=name)
        db.session.add(to_create)
        db.session.commit()
        return code

    @staticmethod
    def get_one(code):
        result = NetworkParameter.query.get(code)
        if not result:
            return None
        return {'network_code': result.network_code, 'name': result.name, 'value': result.value}
    
    @staticmethod
    def get_name(code):
        result = Network.query.get(code)
        if not result:
            return None
        return result.name

    @staticmethod
    def get_all():
        return [{'code': i.code, 'name': i.name, 'created_at': i.created_at}
                for i in Network.query.all()]

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
    def get_one(code):
        result = NetworkParameter.query.get(code)
        if not result:
            return None
        return {'network_code': result.network_code, 'name': result.name, 'value': result.value}
    
    @staticmethod
    def get_by_network_code(code):
        return [{'network_code': i.network_code, 'name': i.name, 'value': i.value}
                for i in NetworkParameter.query.filter_by(network_code=code).all()]

    @staticmethod
    def get_all():
        return [{'network_code': i.network_code, 'name': i.name, 'value': i.value}
                for i in NetworkParameter.query.all()]