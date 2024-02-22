from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

import os

api = Flask(__name__)
api.config['DEBUG'] = True
api.config['FLASK_ENV'] = 'development'
api.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', ''),
    os.getenv('DB_PASSWORD', ''),
    os.getenv('DB_HOST', ''),
    os.getenv('DB_NAME', '')
)
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(api)
cors = CORS(api, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

@api.route("/")
@cross_origin()
def home():
    return "MuSiN api homepage"

from api.routes.executions import executions
api.register_blueprint(executions)

from api.routes.inputs import inputs
api.register_blueprint(inputs)

from api.routes.networks import networks
api.register_blueprint(networks)

from api.routes.plots import plots
api.register_blueprint(plots)

from api.routes.users import users
api.register_blueprint(users)

from api.routes.welcome import welcome
api.register_blueprint(welcome)

@api.before_first_request
def create_tables():
    db.init_app(api)
    db.create_all()

if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True)