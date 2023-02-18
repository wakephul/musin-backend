from flask import Flask, send_file, jsonify, request, make_response
import nest

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

api = Flask(__name__)
api.config['DEBUG'] = True
api.config['FLASK_ENV'] = 'development'

cors = CORS(api, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
db = SQLAlchemy(api)

nest.Install("cerebmodule")

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


@api.route("/")
@cross_origin()
def homepage():
    return "homepage working"

@api.route("/api/", methods=["GET"])
@cross_origin()
def index():
    # nest.Install('cerebmodule')
    # nest.Create('poisson_generator')
    return "API test working"
