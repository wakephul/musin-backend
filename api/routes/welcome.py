from api.api import db
from api.models.executions import Execution, Executiontype, ExecutionExecutiontypeRelationship, ExecutionInputRelationship, ExecutionNetworkRelationship
from api.models.inputs import Input
from api.models.networks import Network, NetworkParameter
from api.models.users import User

from flask import Blueprint

welcome = Blueprint('welcome', __name__)

@welcome.route("/api/")
def api_welcome():
    return "APIs are up and running correctly!"

@welcome.route("/api/delete_db_and_populate_sample")
def sample_db():
    # TODO: if needed, we could backup the db here. For now, we just comment this out in prod
    # import os
    # backup_file = "backup.sql"
    # os.system(f"mysqldump -u <username> -p<password> <database_name> > {backup_file}")
    db.drop_all()
    db.create_all()
    user_code = User.create('test', 'test@test.com', True)
    execution_code = Execution.create('test_exec')
    executiontype_code = Executiontype.create('test_type')
    ExecutionExecutiontypeRelationship.create(execution_code, executiontype_code)
    input_code = Input.create(10.0, 10.0, 50.0, 50.0, 10, 10, 100, 100)
    ExecutionInputRelationship.create(execution_code, input_code)
    network_code = Network.create('test_network')
    NetworkParameter.create(network_code, 'param_test', 1.23)
    ExecutionNetworkRelationship.create(execution_code, network_code)
    return 'DONE!'