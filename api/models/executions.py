from ..api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from ..models.inputs import Input

class Execution(db.Model):

    __tablename__ = "execution"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def create(name):
        to_create = Execution(name)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'id': i.id, 'name': i.name, 'created_at': i.created_at}
                for i in Execution.query.order_by('id').all()]

class Executiontype(db.Model):

    __tablename__ = "executiontype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def create(name: str):
        to_create = Executiontype(name)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'id': i.id, 'name': i.name, 'created_at': i.created_at}
                for i in Executiontype.query.order_by('id').all()]

class ExecutionExecutiontypeRelationship(db.Model):

    __tablename__ = "execution_executiontype_relationship"

    execution_id = Column(Integer, ForeignKey("execution.id"), primary_key=True)
    executiontype_id = Column(Integer, ForeignKey("executiontype.id"), primary_key=True)

    def __init__(self, execution_id: int, executiontype_id: int):
        self.execution_id = execution_id
        self.executiontype_id = executiontype_id

    @staticmethod
    def create(execution_id: int, executiontype_id: int):
        to_create = ExecutionExecutiontypeRelationship(execution_id, executiontype_id)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'execution_id': i.execution_id, 'executiontype_id': i.executiontype_id}
                for i in ExecutionExecutiontypeRelationship.query.all()]

class ExecutionInputRelationship(db.Model):

    __tablename__ = "execution_input_relationship"

    execution_id = Column(Integer, ForeignKey("execution.id"), primary_key=True)
    input_id = Column(Integer, ForeignKey("input.id"), primary_key=True)

    def __init__(self, execution_id: int, input_id: int):
        self.execution_id = execution_id
        self.input_id = input_id

    @staticmethod
    def create(execution_id: int, input_id: int):
        to_create = ExecutionInputRelationship(execution_id, input_id)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'execution_id': i.execution_id, 'input_id': i.input_id}
                for i in ExecutionInputRelationship.query.all()]

class ExecutionNetworkRelationship(db.Model):

    __tablename__ = "execution_network_relationship"

    execution_id = Column(Integer, ForeignKey("execution.id"), primary_key=True)
    network_id = Column(Integer, ForeignKey("network.id"), primary_key=True)

    def __init__(self, execution_id: int, network_id: int):
        self.execution_id = execution_id
        self.network_id = network_id

    @staticmethod
    def create(execution_id: int, network_id: int):
        to_create = ExecutionNetworkRelationship(execution_id, network_id)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'execution_id': i.execution_id, 'network_id': i.network_id}
                for i in ExecutionNetworkRelationship.query.all()]