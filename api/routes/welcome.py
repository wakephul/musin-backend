from ..api import db
from ..models.executions import Execution, Executiontype, ExecutionExecutiontypeRelationship, ExecutionInputRelationship, ExecutionNetworkRelationship
from ..models.inputs import Input
from ..models.networks import Network, NetworkParameter
from ..models.users import User

from flask import Blueprint

welcome = Blueprint('welcome', __name__)

@welcome.route("/api/")
def api_welcome():
    return "APIs are up and running correctly!"

@welcome.route("/api/populate_sample_db")
def sample_db():
    db.session.add(User(username="wakephul", email="wakephul@gmail.com"))
    db.session.commit()
    return 'DONE!'