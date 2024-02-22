from api.api import db
# from api.models.executions import Execution, Executiontype, ExecutionExecutiontypeRelationship, ExecutionInputRelationship, ExecutionNetworkRelationship
from api.models.executions import Execution, Executiontype, ExecutionExecutiontypeRelationship, ExecutionNetworkSideInputRelationship, ExecutionResult
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
    # check_tables = all_tables_empty()
    check_tables = True #to test the sample db
    if (check_tables):
        db.drop_all()
        db.create_all()
        user_code = User.create('test', 'test@test.com', True)
        execution_code = Execution.create('test_exec')
        executiontype_code = Executiontype.create('test_type')
        ExecutionExecutiontypeRelationship.create(execution_code, executiontype_code)
        executiontype_code_2 = Executiontype.create('test_type_1')
        ExecutionExecutiontypeRelationship.create(execution_code, executiontype_code_2)
        input_code = Input.create('test_input', False, 10.0, None, None, 10.0, None, None, 10, None, None, 10, None, None)
        input_code_2 = Input.create('test_input_1', False, 20.0, None, None, 20.0, None, None, 20, None, None, 20, None, None)
        network_code = Network.create('test_network', 2)
        network_code_2 = Network.create('test_network_1', 2)
        NetworkParameter.create(network_code, 'param_test', 1.23)
        NetworkParameter.create(network_code, 'param_test_2', 4.56)
        NetworkParameter.create(network_code_2, 'param_test_3', 7.89)
        ExecutionNetworkSideInputRelationship.create(execution_code, network_code, 1, input_code)
        ExecutionNetworkSideInputRelationship.create(execution_code, network_code, 2, input_code_2)
        ExecutionNetworkSideInputRelationship.create(execution_code, network_code_2, 1, input_code)
        # ExecutionInputRelationship.create(execution_code, input_code)
        # ExecutionInputRelationship.create(execution_code, input_code_2)
        # ExecutionNetworkRelationship.create(execution_code, network_code)
        # ExecutionNetworkRelationship.create(execution_code, network_code_2)
        return 'DONE! You now have a sample database to test everything'
    else:
        return 'Not all tables in the database are empty. Sorry, but I cannot risk to delete possibly important data'


def all_tables_empty():
    models = [Execution, Executiontype, ExecutionExecutiontypeRelationship, ExecutionInputRelationship, ExecutionNetworkRelationship, Input, Network, NetworkParameter, User]
    for model in models:
        result = model.get_all()
        if len(result) > 0:
            return False
    return True