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
        
        input_code_visual = Input.create('visual', False, 10.0, None, None, 10.0, None, None, 10, None, None, 100, None, None)
        input_code_auditory = Input.create('auditory', False, 20.0, None, None, 20.0, None, None, 20, None, None, 200, None, None)

        network_code_cortex = Network.create('cortex', 2)
        NetworkParameter.create(network_code_cortex, 'order', '400.0')
        NetworkParameter.create(network_code_cortex, 'rec_pop', '1.0')
        NetworkParameter.create(network_code_cortex, 'start_stim', '0.0')
        NetworkParameter.create(network_code_cortex, 't_stimulus_end_rev', '100.0')
        NetworkParameter.create(network_code_cortex, 'coh_rev', '0.0')
        NetworkParameter.create(network_code_cortex, 'dt', '0.1')
        NetworkParameter.create(network_code_cortex, 'dt_update', '25.0')
        NetworkParameter.create(network_code_cortex, 'dt_rec', '10.0')
        NetworkParameter.create(network_code_cortex, 'J', '0.04')
        NetworkParameter.create(network_code_cortex, 'eta_ex', '0.96')
        NetworkParameter.create(network_code_cortex, 'eta_in', '0.9')
        NetworkParameter.create(network_code_cortex, 'ratio_stim_rate', '10.0')
        NetworkParameter.create(network_code_cortex, 'std_ratio', '16.0')
        NetworkParameter.create(network_code_cortex, 'std_noise', '200.0')
        NetworkParameter.create(network_code_cortex, 'w_plus', '1.7')
        NetworkParameter.create(network_code_cortex, 'w_minus', '0.8')
        NetworkParameter.create(network_code_cortex, 'w_plus_NMDA', '4.25')
        NetworkParameter.create(network_code_cortex, 'tau_m_ex', '20.0')
        NetworkParameter.create(network_code_cortex, 'tau_m_in', '10.0')
        NetworkParameter.create(network_code_cortex, 'C_m_ex', '500.0')
        NetworkParameter.create(network_code_cortex, 'C_m_in', '200.0')
        NetworkParameter.create(network_code_cortex, 'theta', '-55.0')
        NetworkParameter.create(network_code_cortex, 't_ref_ex', '2.0')
        NetworkParameter.create(network_code_cortex, 't_ref_in', '1.0')
        NetworkParameter.create(network_code_cortex, 'V_membrane', '-70.0')
        NetworkParameter.create(network_code_cortex, 'V_threshold', '-50.0')
        NetworkParameter.create(network_code_cortex, 'V_reset', '-55.0')
        NetworkParameter.create(network_code_cortex, 'tau_syn_noise', '5.0')
        NetworkParameter.create(network_code_cortex, 'tau_syn_AMPA', '2.0')
        NetworkParameter.create(network_code_cortex, 'tau_syn_NMDA', '100.0')
        NetworkParameter.create(network_code_cortex, 'tau_syn_GABA', '5.0')
        NetworkParameter.create(network_code_cortex, 'epsilon_ex_AB_BA', '0.2')
        NetworkParameter.create(network_code_cortex, 'epsilon_ex_reccurent', '0.4')
        NetworkParameter.create(network_code_cortex, 'epsilon_ex_AI_BI', '0.4')
        NetworkParameter.create(network_code_cortex, 'epsilon_in_IA_IB', '0.45')
        NetworkParameter.create(network_code_cortex, 'epsilon_in_recurrent', '0.3')
        NetworkParameter.create(network_code_cortex, 'delay_noise', '0.5')
        NetworkParameter.create(network_code_cortex, 'delay_AMPA', '0.5')
        NetworkParameter.create(network_code_cortex, 'delay_GABA', '0.5')
        NetworkParameter.create(network_code_cortex, 'delay_NMDA', '2.5')
        NetworkParameter.create(network_code_cortex, 'test_types', '3') #this should be a list of integers, divided 'by commas
        NetworkParameter.create(network_code_cortex, 'train_time', '0')
        NetworkParameter.create(network_code_cortex, 'test_time', '6000.0')
        NetworkParameter.create(network_code_cortex, 't_stimulus_start', '0.0')
        NetworkParameter.create(network_code_cortex, 't_stimulus_end', '1000.0')
        NetworkParameter.create(network_code_cortex, 't_stimulus_duration', '1000.0')
        
        network_code_cerebellum = Network.create('cerebellum', 2)
        NetworkParameter.create(network_code_cerebellum, "LTP1", '0.05')
        NetworkParameter.create(network_code_cerebellum, "LTD1", '-6.0')
        NetworkParameter.create(network_code_cerebellum, "Init_PFPC", '4.0')
        NetworkParameter.create(network_code_cerebellum, "LTP2", '1e-5')
        NetworkParameter.create(network_code_cerebellum, "LTD2", '-1e-6')
        NetworkParameter.create(network_code_cerebellum, "Init_MFDCN", '0.07')
        NetworkParameter.create(network_code_cerebellum, "Init_MFDCN_low", '0.06')
        NetworkParameter.create(network_code_cerebellum, "Init_MFDCN_high", '0.11')
        NetworkParameter.create(network_code_cerebellum, "LTP3", '1e-7')
        NetworkParameter.create(network_code_cerebellum, "LTD3", '1e-6')
        NetworkParameter.create(network_code_cerebellum, "Init_PCDCN", '-20.0')
        NetworkParameter.create(network_code_cerebellum, "PLAST1", '1') #boolean
        NetworkParameter.create(network_code_cerebellum, "PLAST2", '0') #boolean
        NetworkParameter.create(network_code_cerebellum, "PLAST3", '0') #boolean
        NetworkParameter.create(network_code_cerebellum, "GR_num", '2000')
        NetworkParameter.create(network_code_cerebellum, "PC_num", '100')
        NetworkParameter.create(network_code_cerebellum, "test_types", "1,2,3")
        NetworkParameter.create(network_code_cerebellum, "train_time", '4500.0')
        NetworkParameter.create(network_code_cerebellum, "test_time", '4500.0')
        NetworkParameter.create(network_code_cerebellum, "t_stimulus_start", '0.0')
        NetworkParameter.create(network_code_cerebellum, "t_stimulus_end", '1000.0')
        NetworkParameter.create(network_code_cerebellum, "t_stimulus_duration", '1000.0')
        NetworkParameter.create(network_code_cerebellum, "number_of_populations", '2')

        ExecutionNetworkSideInputRelationship.create(execution_code, network_code_cortex, 1, input_code_visual)
        ExecutionNetworkSideInputRelationship.create(execution_code, network_code_cortex, 2, input_code_auditory)
        ExecutionNetworkSideInputRelationship.create(execution_code, network_code_cerebellum, 1, input_code_visual)
        ExecutionNetworkSideInputRelationship.create(execution_code, network_code_cerebellum, 2, input_code_auditory)
        
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