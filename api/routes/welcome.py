from api.api import db
from api.models.executions import Execution, ExecutionNetworkSideInputRelationship, ExecutionResult
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
        # if we can, we drop all tables and recreate them, bypassing foreign key constraints
        db.drop_all()
        db.create_all()

        # we populate the db with some sample data
        user_code = User.create('test', 'test@test.com', True)
        execution_code = Execution.create('test_exec')
        input_code = Input.create('visual', False, 10.0, None, None, 10.0, None, None, 10, None, None, 100, None, None)
        input_code_2 = Input.create('auditory', False, 20.0, None, None, 20.0, None, None, 20, None, None, 200, None, None)
        network_code = Network.create('cortex', 2)
        NetworkParameter.create(network_code, 'param_test', 1.23)
        NetworkParameter.create(network_code, 'param_test_2', 4.56)
        network_code_2 = Network.create('cerebellum', 2)
        NetworkParameter.create(network_code_2, 'order', 400.0)
        NetworkParameter.create(network_code_2, 'rec_pop', 1.0)
        NetworkParameter.create(network_code_2, 'start_stim', 0.0)
        NetworkParameter.create(network_code_2, 't_stimulus_end_rev', 100.0)
        NetworkParameter.create(network_code_2, 'coh_rev', 0.0)
        NetworkParameter.create(network_code_2, 'dt', 0.1)
        NetworkParameter.create(network_code_2, 'dt_update', 25.0)
        NetworkParameter.create(network_code_2, 'dt_rec', 10.0)
        NetworkParameter.create(network_code_2, 'J', 0.04)
        NetworkParameter.create(network_code_2, 'eta_ex', 0.96)
        NetworkParameter.create(network_code_2, 'eta_in', 0.9)
        NetworkParameter.create(network_code_2, 'ratio_stim_rate', 10.0)
        NetworkParameter.create(network_code_2, 'std_ratio', 16.0)
        NetworkParameter.create(network_code_2, 'std_noise', 200.0)
        NetworkParameter.create(network_code_2, 'w_plus', 1.7)
        NetworkParameter.create(network_code_2, 'w_minus', 0.8)
        NetworkParameter.create(network_code_2, 'w_plus_NMDA', 4.25)
        NetworkParameter.create(network_code_2, 'tau_m_ex', 20.0)
        NetworkParameter.create(network_code_2, 'tau_m_in', 10.0)
        NetworkParameter.create(network_code_2, 'C_m_ex', 500.0)
        NetworkParameter.create(network_code_2, 'C_m_in', 200.0)
        NetworkParameter.create(network_code_2, 'theta', -55.0)
        NetworkParameter.create(network_code_2, 't_ref_ex', 2.0)
        NetworkParameter.create(network_code_2, 't_ref_in', 1.0)
        NetworkParameter.create(network_code_2, 'V_membrane', -70.0)
        NetworkParameter.create(network_code_2, 'V_threshold', -50.0)
        NetworkParameter.create(network_code_2, 'V_reset', -55.0)
        NetworkParameter.create(network_code_2, 'tau_syn_noise', 5.0)
        NetworkParameter.create(network_code_2, 'tau_syn_AMPA', 2.0)
        NetworkParameter.create(network_code_2, 'tau_syn_NMDA', 100.0)
        NetworkParameter.create(network_code_2, 'tau_syn_GABA', 5.0)
        NetworkParameter.create(network_code_2, 'epsilon_ex_AB_BA', 0.2)
        NetworkParameter.create(network_code_2, 'epsilon_ex_reccurent', 0.4)
        NetworkParameter.create(network_code_2, 'epsilon_ex_AI_BI', 0.4)
        NetworkParameter.create(network_code_2, 'epsilon_in_IA_IB', 0.45)
        NetworkParameter.create(network_code_2, 'epsilon_in_recurrent', 0.3)
        NetworkParameter.create(network_code_2, 'delay_noise', 0.5)
        NetworkParameter.create(network_code_2, 'delay_AMPA', 0.5)
        NetworkParameter.create(network_code_2, 'delay_GABA', 0.5)
        NetworkParameter.create(network_code_2, 'delay_NMDA', 2.5)
        NetworkParameter.create(network_code_2, 'test_types', '3') #this should be a list of integers, divided by commas
        NetworkParameter.create(network_code_2, 'train_time', 0)
        NetworkParameter.create(network_code_2, 'test_time', 6000.0)
        NetworkParameter.create(network_code_2, 't_stimulus_start', 0.0)
        NetworkParameter.create(network_code_2, 't_stimulus_end', 1000.0)
        NetworkParameter.create(network_code_2, 't_stimulus_duration', 1000.0)

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
    models = [Execution, Input, Network, NetworkParameter, User, ExecutionNetworkSideInputRelationship, ExecutionResult]
    for model in models:
        result = model.get_all()
        if len(result) > 0:
            return False
    return True