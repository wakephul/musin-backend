import uuid

from api.api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float

class Execution(db.Model):

    __tablename__ = "execution"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
        return [{'code': i.code, 'name': i.name, 'created_at': i.created_at}
                for i in Execution.query.all()]

class Executiontype(db.Model):

    __tablename__ = "executiontype"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    @staticmethod
    def create(name: str):
        code = str(uuid.uuid4())
        to_create = Executiontype(code=code, name=name)
        db.session.add(to_create)
        db.session.commit()
        return code

    @staticmethod
    def get_one(code):
        result = Executiontype.query.get(code)
        if not result:
            return None
        return {'code': result.code, 'name': result.name, 'created_at': result.created_at}
    
    @staticmethod
    def get_name(code):
        result = Executiontype.query.get(code)
        if not result:
            return None
        return result.name

    @staticmethod
    def get_all():
        return [{'code': i.code, 'name': i.name, 'created_at': i.created_at}
                for i in Executiontype.query.all()]

class ExecutionExecutiontypeRelationship(db.Model):

    __tablename__ = "execution_executiontype_relationship"

    execution_code = Column(String(36), ForeignKey("execution.code"), primary_key=True)
    executiontype_code = Column(String(36), ForeignKey("executiontype.code"), primary_key=True)

    def __init__(self, execution_code: str, executiontype_code: str):
        self.execution_code = execution_code
        self.executiontype_code = executiontype_code

    @staticmethod
    def create(execution_code: str, executiontype_code: str):
        to_create = ExecutionExecutiontypeRelationship(execution_code, executiontype_code)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get_by_execution_code(code):
        return [{'execution_code': i.execution_code, 'executiontype_code': i.executiontype_code}
                for i in ExecutionExecutiontypeRelationship.query.filter_by(execution_code=code).all()]
    
    @staticmethod
    def get_by_executiontype_code(code):
        return [{'execution_code': i.execution_code, 'executiontype_code': i.executiontype_code}
                for i in ExecutionExecutiontypeRelationship.query.filter_by(executiontype_code=code).all()]
    
    @staticmethod
    def get_all():
        return [{'execution_code': i.execution_code, 'executiontype_code': i.executiontype_code}
                for i in ExecutionExecutiontypeRelationship.query.all()]

# class ExecutionInputRelationship(db.Model):

#     __tablename__ = "execution_input_relationship"

#     execution_code = Column(String(36), ForeignKey("execution.code"), primary_key=True)
#     input_code = Column(String(36), ForeignKey("input.code"), primary_key=True)

#     def __init__(self, execution_code: str, input_code: str):
#         self.execution_code = execution_code
#         self.input_code = input_code

#     @staticmethod
#     def create(execution_code: str, input_code: str):
#         to_create = ExecutionInputRelationship(execution_code, input_code)
#         db.session.add(to_create)
#         db.session.commit()

#     @staticmethod
#     def get_by_execution_code(code):
#         return [{'execution_code': i.execution_code, 'input_code': i.input_code}
#                 for i in ExecutionInputRelationship.query.filter_by(execution_code=code).all()]
    
#     @staticmethod
#     def get_by_input_code(code):
#         return [{'execution_code': i.execution_code, 'input_code': i.input_code}
#                 for i in ExecutionInputRelationship.query.filter_by(input_code=code).all()]

#     @staticmethod
#     def get_all():
#         return [{'execution_code': i.execution_code, 'input_code': i.input_code}
#                 for i in ExecutionInputRelationship.query.all()]

# class ExecutionNetworkRelationship(db.Model):

#     __tablename__ = "execution_network_relationship"

#     execution_code = Column(String(36), ForeignKey("execution.code"), primary_key=True)
#     network_code = Column(String(36), ForeignKey("network.code"), primary_key=True)

#     def __init__(self, execution_code: str, network_code: str):
#         self.execution_code = execution_code
#         self.network_code = network_code

#     @staticmethod
#     def create(execution_code: str, network_code: str):
#         to_create = ExecutionNetworkRelationship(execution_code, network_code)
#         db.session.add(to_create)
#         db.session.commit()

#     @staticmethod
#     def get_by_execution_code(code):
#         return [{'execution_code': i.execution_code, 'network_code': i.network_code}
#                 for i in ExecutionNetworkRelationship.query.filter_by(execution_code=code).all()]
    
#     @staticmethod
#     def get_by_network_code(code):
#         return [{'execution_code': i.execution_code, 'network_code': i.network_code}
#                 for i in ExecutionNetworkRelationship.query.filter_by(network_code=code).all()]

#     @staticmethod
#     def get_all():
#         return [{'execution_code': i.execution_code, 'network_code': i.network_code}
#                 for i in ExecutionNetworkRelationship.query.all()]
    
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
