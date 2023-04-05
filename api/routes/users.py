from flask import Blueprint, jsonify
from flask_cors import cross_origin
from api.api import db

from api.models.users import User

users = Blueprint('users', __name__)

@users.route("/api/users/add/")
@cross_origin()
def add():
    User.create("test", "prova@test.it", False)
    return "Correctly added user to db"

@users.route("/api/users/list/")
@cross_origin()
def list():
    users = User.get_all()
    return jsonify(users)