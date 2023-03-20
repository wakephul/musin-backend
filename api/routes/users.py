from flask import Blueprint
from flask_cors import cross_origin
from ..api import db

from ..models.users import User

users = Blueprint('users', __name__)

@users.route("/api/users/add/")
@cross_origin()
def add():
    db.session.add(User(username="wakephul", email="wakephul@gmail.com"))
    db.session.commit()
    return "Correctly added user to db"

@users.route("/api/users/list/")
@cross_origin()
def list():
    users = db.session.query(User).all()
    u = ', '.join(str(user.username)+' - '+str(user.email) for user in users)
    return u