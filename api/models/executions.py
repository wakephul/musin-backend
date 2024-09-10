import uuid

from api.api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float

class Execution(db.Model):

    __tablename__ = "execution"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    @staticmethod
    def create(name):
        code = str(uuid.uuid4())
        to_create = Execution(code=code, name=name)
        db.session.add(to_create)
        db.session.commit()
        return code

    @staticmethod
    def get_one(code):
        result = Execution.query.get(code)
        if not result:
            return None
        return {'code': result.code, 'name': result.name, 'created_at': result.created_at}
    
    @staticmethod
    def get_execution_details(code):
        result = Execution.query.get(code)
        if not result:
            return None
        execution = {'code': result.code, 'name': result.name, 'created_at': result.created_at}
        return execution

    @staticmethod
    def get_all():
        executions = Execution.query.all()
        executions = sorted(executions, key=lambda x: x.created_at, reverse=True)
        return [{'code': i.code, 'name': i.name, 'created_at': i.created_at}
                for i in executions]
    
    @staticmethod
    def update(code, finished_at):
        execution = Execution.query.get(code)
        execution.finished_at = finished_at
        db.session.commit()
        return {'code': execution.code, 'name': execution.name, 'created_at': execution.created_at, 'finished_at': execution.finished_at}
    
class ExecutionNetworkSideInputRelationship(db.Model):
    
        __tablename__ = "execution_network_side_input_relationship"
    
        execution_code = Column(String(36), ForeignKey("execution.code"), primary_key=True)
        network_code = Column(String(36), ForeignKey("network.code"), primary_key=True)
        side = Column(Integer, primary_key=True)
        input_code = Column(String(36), ForeignKey("input.code"), primary_key=True)
    
        def __init__(self, execution_code: str, network_code: str, side: int, input_code: str):
            self.execution_code = execution_code
            self.network_code = network_code
            self.side = side
            self.input_code = input_code
    
        @staticmethod
        def create(execution_code: str, network_code: str, side: int, input_code: str):
            to_create = ExecutionNetworkSideInputRelationship(execution_code, network_code, side, input_code)
            db.session.add(to_create)
            db.session.commit()
    
        @staticmethod
        def get_by_execution_code(code):
            return [{'execution_code': i.execution_code, 'network_code': i.network_code, 'side': i.side, 'input_code': i.input_code}
                    for i in ExecutionNetworkSideInputRelationship.query.filter_by(execution_code=code).all()]
        
        @staticmethod
        def get_by_network_code(code):
            return [{'execution_code': i.execution_code, 'network_code': i.network_code, 'side': i.side, 'input_code': i.input_code}
                    for i in ExecutionNetworkSideInputRelationship.query.filter_by(network_code=code).all()]
        
        @staticmethod
        def get_all():
            return [{'execution_code': i.execution_code, 'network_code': i.network_code, 'side': i.side, 'input_code': i.input_code}
                    for i in ExecutionNetworkSideInputRelationship.query.all()]
class ExecutionResult(db.Model):
    id = Column(Integer, primary_key=True)
    result_path = Column(String(100))
    image_path = Column(String(100))

    def __init__(self, result_path: str, image_path: str):
        self.result_path = result_path
        self.image_path = image_path
    
    @staticmethod
    def create(result_path: str, image_path: str):
        to_create = ExecutionResult(result_path, image_path)
        db.session.add(to_create)
        db.session.commit()
        return to_create.id
    
    @staticmethod
    def get_one(id):
        result = ExecutionResult.query.get(id)
        if not result:
            return None
        return {'id': result.id, 'result_path': result.result_path, 'image_path': result.image_path}
    
    @staticmethod
    def get_all():
        return [{'id': i.id, 'result_path': i.result_path, 'image_path': i.image_path}
                for i in ExecutionResult.query.all()]
