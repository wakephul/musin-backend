import uuid

from api.api import db

from sqlalchemy.sql import func

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float

class User(db.Model):

    __tablename__ = "user"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    username = Column(String(100), nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    active = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, code: str, username: str, email: str, active: bool):
        self.code = code
        self.username = username
        self.email = email
        self.active = active

    @staticmethod
    def create(username: str, email: str, active: bool):
        code = str(uuid.uuid4())
        to_create = User(code=code, username=username, email=email, active=active)
        db.session.add(to_create)
        db.session.commit()
        return code
    
    @staticmethod
    def get_one(code):
        result = User.query.get(code)
        if not result:
            return None
        return {'code': result.code, 'username': result.username, 'email': result.email, 'active': result.active, 'created_at': result.created_at}

    @staticmethod
    def get_all():
        return [{'code': i.code, 'username': i.username, 'email': i.email, 'active': i.active, 'created_at': i.created_at}
                for i in User.query.all()]