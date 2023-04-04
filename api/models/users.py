from ..api import db

from sqlalchemy.sql import func

class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, username: str, email: str, active: bool):
        self.username = username
        self.email = email
        self.active = active

    @staticmethod
    def create(name: str, email: str, active: bool):
        to_create = User(name, email, active)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get_all():
        return [{'id': i.id, 'username': i.username, 'email': i.email, 'active': i.active, 'created_at': i.created_at}
                for i in User.query.order_by('id').all()]